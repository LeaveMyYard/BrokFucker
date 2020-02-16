import sqlite3
import os
import hashlib
from datetime import datetime
from lib.util.exceptions import RegistrationError

class DatadaseHandler:
    def __init__(self, file_name: str = 'database.db'):
        
        #Test if 'data' folder exists. If not, create it.
        directory = 'data'
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)

        #All database files will be located at data folder
        self.conn = sqlite3.connect(f'{directory}/{file_name}')
        self.cursor = self.conn.cursor()
        self.__init_tables()

    def __init_tables(self):

        #Load tables init sql request from 'lib/sql/init_tables.sql' and execute it. 
        request_file = open('lib/sql/init_tables.sql', mode='r')
        self.cursor.execute(request_file.read())
        self.conn.commit()

    def check_user_exists(self, email: str) -> bool:
        '''
            Returns True if user with corresponding email exists, False otherwise
        '''

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchall()
        
        return res != []

    def check_password(self, email: str, password: str) -> bool:
        '''
            Return True if the email and password pair is correct.
            If password is incorrect, returns False
            If email is not registerd, will return False also.
        '''

        if not self.check_user_exists(email):
            return False

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()
        
        return res[2] == hashlib.sha256(password.encode('utf-8')).hexdigest()


    def create_user(self, email: str, password: str) -> bool:
        '''
            This method will add a new user using email or password.
            If something is wrong, it will raise RegistrationError with the message of an error.
        '''

        if self.check_user_exists(email):
            raise RegistrationError(-1200, 'Email is already in use.')

        if len(password) < 8:
            raise RegistrationError(-1201, 'A password size is less than 8.')

        if len(password) > 32:
            raise RegistrationError(-1201, 'A password size is bigger than 32.')

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        reg_date = datetime.now()
        self.cursor.execute(
            f"INSERT INTO Users (`email`, `password`, `reg_date`)"
            f"VALUES ('{email}', '{password_hash}', '{reg_date}')"
        )
        self.conn.commit()