import psycopg2
   
class Database:
    '''This class creates and interacts with a database.'''
    
    def check_exists(self):
        ''' Check if the database exists, returning True/False'''
            
        does_exist = False
            
        try:
            conn = psycopg2.connect(host=self.db_host, user=self.db_user, password=self.db_passwd, port=self.db_port)
            cursor = conn.cursor()
                
            cursor.execute(f"SELECT exists(SELECT datname FROM pg_catalog.pg_database WHERE datname = '{self.db_name}')")
            does_exist = cursor.fetchone()[0]   
                            
            cursor.close()
            conn.close()
                
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            
        return(does_exist)
   
    def __init__(self, name, tables):
        ''' Initialize database variables and create the database if it doesn't already exist.
            Parameters: name-   name of the database to be created.
                        tables- list of SQL queries necessary to create desired tables for the database.'''
                        
        self.db_name = name
        self.db_host = 'localhost'
        self.db_user = 'postgres'
        self.db_passwd = 'Le@rnDB'
        self.db_port = '5432'
    
        self.create_db = f"CREATE DATABASE {self.db_name} WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'English_United States.1252' LC_CTYPE = 'English_United States.1252' LOCALE_PROVIDER = 'libc' TABLESPACE = pg_default CONNECTION LIMIT = -1 IS_TEMPLATE = False;"
        self.create_tables = tables
        self.db_exists = self.check_exists()
        ''' CREATE TABLE IF NOT EXISTS public.msg_history(msg_index integer NOT NULL GENERATED ALWAYS AS IDENTITY ( CYCLE INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ), room text COLLATE pg_catalog."default" NOT NULL, username text COLLATE pg_catalog."default" NOT NULL, msg text COLLATE pg_catalog."default" NOT NULL, msg_time timestamp with time zone NOT NULL, CONSTRAINT msg_history_pkey PRIMARY KEY (msg_index))
            CREATE TABLE IF NOT EXISTS public.sys_history(msg text COLLATE pg_catalog."default" NOT NULL, msg_time timestamp with time zone NOT NULL)
        '''
                            
        conn = psycopg2.connect(host = self.db_host,
                                user = self.db_user,
                                password = self.db_passwd,
                                port = self.db_port)
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            if self.db_exists == False:
                cursor.execute(self.create_db)
            #cursor.close()
            #conn.close()
            conn2 = psycopg2.connect(database = self.db_name,
                                     host = self.db_host,
                                     user = self.db_user,
                                     password = self.db_passwd,
                                     port = self.db_port)
            conn2.autocommit = True
            cursor2 = conn2.cursor()
            for sql in self.create_tables:
                cursor2.execute(sql)
            cursor2.close()
            conn2.close()
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)
        finally:
            cursor.close()
            conn.close()
   
    def get_data(self, table, data, key, value):
        ''' This will return the selected data from the database in a list.
            Parameters: table-  string; name of the table containing the data.
                        data-   string; name of the data to return.
                        key-    string; name of the column used to identify the desired data.
                        value-  string; value used to identify the desired data.
            Example:    You want to know all the types of fruit a store has for sale in their grocery aisles.
                        fruit = get_data(store_inventory, items, groceries, fruit)'''
        content = []
        
        conn = psycopg2.connect(database = self.db_name,
                                host = self.db_host,
                                user = self.db_user,
                                password = self.db_passwd,
                                port = self.db_port)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT {data} FROM {table} WHERE {key} = '{value}'")
        tmp_hold = cursor.fetchall()
        
        for i in tmp_hold:
            content.append(f'{i[0]}')
        
        cursor.close()
        conn.close()
        return (content)
    
    def save_data(self, table, column, data):
        '''This will save data to the database.'''

        conn = psycopg2.connect(database = self.db_name,
                                host = self.db_host,
                                user = self.db_user,
                                password = self.db_passwd,
                                port = self.db_port)
        cursor = conn.cursor()
        
        for i in range(len(data)):
            data[i] = f"'{data[i]}'"

        #print(f"INSERT INTO {table}({', '.join(column)}) VALUES ({', '.join(data)})")

        cursor.execute(f"INSERT INTO {table}({', '.join(column)}) VALUES ({', '.join(data)})")
        conn.commit()
        
        cursor.close()
        conn.close()
                    
