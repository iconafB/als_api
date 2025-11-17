import json
import requests
import os
from datetime import datetime
from fastapi import status,HTTPException,Depends
from sqlmodel import Session,text
from settings.Settings import get_settings
import pandas as pd
from utils.logger import define_logger
from database.pings_db_connect import get_pings_session_db   
import csv

PING_URL="https://ss.dedago.com/api/iconping"

PING_HEADER={"content-type": "application/json"}

pings_logger=define_logger("als pings logs","logs/pings.log")

def convert_numbers_to_csv(numbers_to_ping: list, dir: str, file_name: str) -> None:
    series = pd.Series(numbers_to_ping, name="telnr")
    os.makedirs(dir, exist_ok=True)
    file_path = os.path.join(dir, file_name)
    series.to_csv(file_path, index=False, header=True)



def process_numbers(numbersToPing):
    # Ensure the list never exceeds 300,000 elements
    print('FIRST = ', len(numbersToPing))
    if len(numbersToPing) > 300000:
        numbersToPing = numbersToPing[:300000]

    print('SECOND = ', len(numbersToPing))
    # Determine the split point
    midpoint = len(numbersToPing) // 2
    send_pings_kuda(numbersToPing[:midpoint])  # First 150K to kuda()
    today_date = datetime.today().strftime("%Y-%m-%d")

    file_name = today_date + ".csv"
    convert_numbers_to_csv(numbersToPing[:midpoint], "kuda_ping_data/", file_name)
    convert_numbers_to_csv(numbersToPing[midpoint:], "troy_ping_data/", file_name)  # change directory name

    send_pings_troy("troy_ping_data/", file_name)

    slack.Logs(
        f"Splitting: Sending first {midpoint} to kuda() and the rest {midpoint} to troy()").slack_message()

    print(f"Splitting: Sending first {midpoint} to kuda() and the rest {midpoint} to troy()")


def filter_numbers(totalnumbers, totaldblist):
    """
    Filters totalnumbers to return only the tuples where element[0] (cell number) exists in totaldblist.

    :param totalnumbers: List of tuples, where element[0] is the cell number.
    :param totaldblist: List containing the cell numbers to filter by.
    :return: Filtered list of tuples.
    """
    db_set = set(totaldblist)  # Convert list to set for faster lookups
    print('DB SET = ', len(db_set))
    print('TXT SET = ', len(totalnumbers))
    return [tup for tup in totalnumbers if tup[0] in db_set]


def get_list_from_file(file_path: str):
    # file_path = "C:/Users/Administrator/Desktop/Ping_Origin/troy_ping_data/2025-03-20.csv"

    # Read the CSV file and store numbers in a list
    telnr_list = []
    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            telnr_list.append(row["telnr"])

    return telnr_list


def fetch_data(read_stmt,session:Session):
    # Database connection parameters
    db_params = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'new2025_strong_password20@676',
        'host': '102.211.29.157',
        'port': 5433
    }

    try:
        # Establish connection
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Execute the provided SQL query
        cursor.execute(read_stmt)

        # Fetch all rows
        rows = cursor.fetchall()

        # Print the results
        list_to_send = []
        for row in rows:
            # print(row)
            list_to_send.append(row[0])

        # Close cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error with fetching data TO ping: {e}")

    if len(list_to_send) > 0:
        return list_to_send
    else:
        return 'No numbers avails to send'


def send_pings_to_dedago(list_numbers:None):
    try:
        timestamp=datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
        payload={"datetostart":timestamp,"numbers":list_numbers}
        if not list_numbers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No numbers uploaded for ping service")
        dedago_response=requests('POST',url=PING_URL,data=json.dumps(payload),timeout=700)
        return dedago_response
    except Exception as e:
        pings_logger.exception(f"an exception occurred while sending pings to dedago:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
    

def send_pings_to_kuda(records:None):

    try:
        list_of_nums=records

        batch_size=2000
        now=datetime.now()

        timestamp=str(now)[0:16]

        headers = {"content-type": "application/json"}

        hopper_level_payload = {"server": 2}

        hopper_level_request=requests.get(url=f"{get_settings().hopper_level_check_url}",data=json.dumps(hopper_level_payload),verify=True,headers=headers,timeout=30,auth=(get_settings().send_pings_to_kuda_username,get_settings().send_pings_to_kuda_password))
        
        if hopper_level_request.status_code!=200:

            return hopper_level_request.json()
        
        elif hopper_level_request.status_code==200:

            data_hopper=hopper_level_request.json()

            hopper_level_value=data_hopper.get('hopper',0)

            if hopper_level_value>=100000:
                hopper_level_message=f"Server 2  has {hopper_level_value} in the hopper ping will be delayed"
                hopper_level_delay_message=f"Server 2  has {hopper_level_value} in the hopper ping will be delayed till the hopper is cleared"
                pings_logger.info(hopper_level_message)
                pings_logger.info(hopper_level_delay_message)

                return {hopper_level_message:hopper_level_message,hopper_level_delay_message:hopper_level_delay_message}
            else:
                size_of_ping=len(list_of_nums)-hopper_level_value
                for i in range(0,size_of_ping,batch_size):
                    batch=list_of_nums[i: i+batch_size]
                    payload={"datetostart":timestamp,"numbers":batch,"server":2}
                    ping_request=requests.post(get_settings().icon_ping_url,data=json.dumps(payload),verify=True,headers=headers,timeout=12000,auth=(get_settings().send_pings_to_kuda_username,get_settings().send_pings_to_kuda_password))

                    if ping_request!=200:
                        pings_logger.error(f"{ping_request.json()}")

                        return {"message":"Error with Kuda's Ping Service"}
                    
                return {"message":f"{records}"}
    except Exception as e:
        pings_logger.critical(f"{str(e)}")

        return {"error_message":f"{str(e)}"}

#send pings to troy

def send_pings_to_troy(dir:str,filename:str):

    try:
        file_path=os.path.join(dir,filename)
        #raise an error if the file is read again

        df=pd.read_csv(file_path)

        pings_length=len(df)

        batch_name=filename.split(".")[0]

        data={"batch_name":batch_name,"token":get_settings().send_pings_to_troy_token}

        files = {"data_file": ("file_name.csv", open(file_path, "rb"), "text/csv")}

        response=requests.post(url=get_settings().send_pings_to_troy_url,data=data,files=files,timeout=3000)

        if response.status_code!=200:
            pings_logger.error(f"f{response.raise_for_status}")
            pings_logger.critical(f"{response.json()}")
            return {"message":f"error sending pings to troy"}
        
        elif response.status_code==200:

            pings_logger.info(f"successfully sent {pings_length} to Troy with batch name:{batch_name}")

            return {"message":f"successfully sent {pings_length} to Troy with batch name:{batch_name}"}
        else:
            pings_logger.critical(f"internal server error,status code:{response.status_code}")
            return {"message":"Internal Server Error","status_code":response.status_code}
    
    except Exception as e:
        pings_logger.critical(f"f{str(e)}")
        return {"message":f"{str(e)}"}


def classify_model_type(session:Session=Depends(get_pings_session_db)):
    try:
        today_date=datetime.today().strftime("%Y-%m-%d")

        update_sql = f"""
            UPDATE origin.pinged_output_status 
            SET model_output = 'HIGH'
            WHERE 
            (DATE(pinged_date) = '{today_date}') 
            AND
            ((status = 'ANSWER' AND duration::INTEGER > 4)
            OR (status = 'BUSY' AND duration::INTEGER <= 4)
            OR (status = 'POS'));
        """
        
        result=session.exec(text(update_sql),{"today_date":today_date})
        #questionable
        row_count=result.rowcount
        session.commit()
        return {"message":f"successfully updated {row_count}:HIGH CLASSIFICATION"}
    
    except Exception as e:
        session.rollback()
        session.close()
        pings_logger.critical(f"{str(e)}")
        return {"error_message":f"{str(e)}"}
    

def send_numbers_6am():
    return True
