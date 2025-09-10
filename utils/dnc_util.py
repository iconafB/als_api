import mysql.connector
#connect to the mysql database
#this method fetches dnc numbers from the global dnc or the king price database depending on the string that is passed
#this string should be global_dnc or kp_dnc

def dnc_list_of_numbers(type_of_database:str):
    
    try:
        #dnc database connection 
        mysqldb_connection=mysql.connector.connect(host='localhost',user="root",password="scriptbit",database="dnc_db")
        #sql query to fetch all the number from the dn table
        dnc_sql_query=f"select Number from {type_of_database}"
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
        print("print an exception")
        print(e)
        return 
    #close the database connection
    finally:
        if mysqldb_connection.is_connected():
            mysqldb_connection.close()
            my_cursor.close()
    
    return new_dnc_list

def send_dnc_list_to_db():

    return True