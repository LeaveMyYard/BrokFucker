import sqlite3
import os
import pandas as pd

class DatabaseInterface:
    def __init__(self, file_name: str = 'database.db'):
        
        #Test if 'data' folder exists. If not, create it.
        directory = 'data'
        self.create_directory_if_not_exists(directory)

        #All database files will be located at data folder
        self.conn = sqlite3.connect(f'{directory}/{file_name}')
        self.cursor = self.conn.cursor()

    @staticmethod
    def create_directory_if_not_exists(directory):
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)

    def execute_request(self, request) -> bool:
        try:
            self.cursor.execute(request)
        except Exception as e:
            print(e)
            return False
        else:
            df = pd.DataFrame(self.cursor.fetchall())
            print(df)
            return True
        
    def commit(self):
        self.conn.commit()

    def get_input_true_false(self, text) -> bool:
        v = input(f"{text} y/[n]")
        if v == 'y' or v == 'Y' or v == '':
            return True
        elif v == 'n' or v == 'N':
            return False
        else:
            print(f'Invalid value, try again...')
            return self.get_input_true_false(text)

if __name__ == "__main__":
    interface = DatabaseInterface()

    while True:
        if interface.execute_request(input(">>> Waiting for your next request:\n")):
            if interface.get_input_true_false(">>> Do you want to commit your changes?"):
                interface.commit()
            print('\n\n')

        