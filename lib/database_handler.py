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
        self.cursor.executescript(request_file.read())
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
            f"SELECT `password` FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()
        
        return res[0] == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def is_moderator(self, email: str) -> bool:
        if not self.check_user_exists(email):
            return False

        self.cursor.execute(
            f"SELECT `type` FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()

        return res[0] == 1

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
            f"INSERT INTO Users (`email`, `password`, `type`, `reg_date`)"
            f"VALUES ('{email}', '{password_hash}', '0', '{reg_date}')"
        )
        self.conn.commit()

    def get_user_data(self, email) -> bool:
        if not self.check_user_exists(email):
            raise ValueError

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()

        return {
            'email': res[0],
            'type': 'moderator' if res[2] == 1 else 'user',
            'registration_date': res[3],
            'name': res[4],
            'phone_number': res[5]
        }

    def create_new_lot(
        self, 
        user,
        name,
        amount,
        currency,
        term,
        return_way,
        security,
        percentage,
        form
    ):
        date = datetime.now()
        self.cursor.execute(
            f"INSERT INTO Lots (`date`, `name`, `user`, `amount`, `currency`, `term`, `return_way`, `security`, `percentage`, `form`, `security_checked`, `guarantee_percentage`, `confirmed`)"
            f"VALUES ('{date}', '{name}', '{user}', '{amount}', '{currency}', '{term}', '{return_way}', '{security}', '{percentage}', '{form}', 'False', '0', 'False')"
        )

        self.cursor.execute(
            f"SELECT `id` FROM Lots WHERE `date` = '{date}'"
        )
        lot_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            f"SELECT `user_lots` FROM UsersLots WHERE `email` = '{user}'"
        )
        
        res: list = eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.add(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `user_lots` = '{res}' WHERE `email` = '{user}'"
        )

        self.conn.commit()

    def approve_lot(self, lot_id):
        self.cursor.execute(
            f"UPDATE Lots SET `confirmed` = 'True' WHERE `id` = '{lot_id}'"
        )
        self.conn.commit()

    def get_lot(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `id` = '{lot_id}'"
        )
        lot = self.cursor.fetchone()

        return {
            'id': lot[0],
            'date': lot[1],
            'name': lot[2],
            'user': lot[3],
            'amount': lot[4],
            'currency': lot[5],
            'term': lot[6],
            'return_way': lot[7],
            'security': lot[8],
            'percentage': lot[9],
            'form': lot[10],
            'security_checked': eval(lot[11]),
            'guarantee_percentage': lot[12]
        }

    def get_all_approved_lots(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `confirmed` = 'True'"
        )

        return [
            {
                'id': lot[0],
                'date': lot[1],
                'name': lot[2],
                'user': lot[3],
                'amount': lot[4],
                'currency': lot[5],
                'term': lot[6],
                'return_way': lot[7],
                'security': lot[8],
                'percentage': lot[9],
                'form': lot[10],
                'security_checked': eval(lot[11]),
                'guarantee_percentage': lot[12]
            }
            for lot in self.cursor.fetchall()
        ]

    def get_all_unapproved_lots(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `confirmed` = 'False'"
        )

        return [
            {
                'id': lot[0],
                'date': lot[1],
                'name': lot[2],
                'user': lot[3],
                'amount': lot[4],
                'currency': lot[5],
                'term': lot[6],
                'return_way': lot[7],
                'security': lot[8],
                'percentage': lot[9],
                'form': lot[10],
                'security_checked': eval(lot[11]),
                'guarantee_percentage': lot[12]
            }
            for lot in self.cursor.fetchall()
        ]

    def set_security_checked(self, lot_id, checked):
        self.cursor.execute(
            f"UPDATE Lots SET `security_checked` = '{checked}' WHERE `id` = '{lot_id}'"
        )
        self.conn.commit()

    def add_lot_to_favorites(self, email, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = '{email}'"
        )

        res: list = eval(self.cursor.fetchone()[0])
        if lot_id not in res:
            res.append(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = '{res}' WHERE `email` = '{email}'"
        )
        self.conn.commit()

    def remove_lot_from_favorites(self, email, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = '{email}'"
        )
        
        res: list = eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.remove(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = '{res}' WHERE `email` = '{email}'"
        )
        self.conn.commit()

    def get_favorites(self, email):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = '{email}'"
        )
        
        res: list = eval(self.cursor.fetchone()[0])

        return [self.get_lot(lot_id) for lot_id in reversed(res)]