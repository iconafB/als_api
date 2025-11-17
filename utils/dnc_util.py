import mysql.connector

from fastapi import HTTPException,status
from utils.logger import define_logger

dnc_logger=define_logger("als dnc logs","logs/dnc_route.log")

#connect to the mysql database
#this method fetches dnc numbers from the global dnc or the king price database depending on the string that is passed
#this string should be global_dnc or kp_dnc



def dnc_list_numbers():
    
    try:
        #dnc database connection 
        mysqldb_connection=mysql.connector.connect(host='localhost',user="root",password="scriptbit",database="dnc_db")
        #sql query to fetch all the number from the dn table
        dnc_sql_query=f"select Number from global_dnc"

        my_cursor=mysqldb_connection.cursor(buffered=True)
        #execute the sql query
        my_cursor.execute(dnc_sql_query)
        records=my_cursor.fetchall()
        #list comprehension to populate the dnc list 
        dnc_list=[]
        #new populated dnc list
        new_dnc_list=[dnc_list.append(value[0]) for value in records]

    except mysql.connector.Error as e:
        #logs will take care of this
        print("log the error")
        dnc_logger.error(f"{str(e)}")
        return 
    
    #close the database connection
    finally:
        if mysqldb_connection.is_connected():
            mysqldb_connection.close()
            my_cursor.close()
    
    return new_dnc_list



def send_dnc_list_to_db(dnc_list:list,camp_code:str):

    try:
        mysqldb_connection=mysql.connector.connect(host='localhost',user="root",password="scriptbit",database="dnc_db")
        
        count=0

        for number in dnc_list:

            sql_select_query=f"select Number from {camp_code}_dnc where Number={number}"
            cursor=mysqldb_connection.cursor(buffered=True)
            cursor.execute(sql_select_query)
            numbers_present_on_dnc=cursor.rowcount()
            
            if numbers_present_on_dnc==0:
                count+=1
                mysql_insert_query=f"INSERT INTO {camp_code}_dnc(Number) VALUES('{number}')" 
                cursor.execute(mysql_insert_query)
                mysqldb_connection.commit()
        
        cursor.close()

        dnc_logger.info(f"{len(dnc_list)} numbers added to the dnc database(db)")

    except mysql.connector.Error as e:
        dnc_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"error connecting to the dnc mysql db")
    
    finally:
        mysqldb_connection.close()
        cursor.close()

