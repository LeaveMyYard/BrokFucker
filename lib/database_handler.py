import sqlite3
import os
import hashlib
import base64
from enum import Enum
from typing import Union, Tuple
from flask import request
from datetime import datetime, timedelta
import lib.util.exceptions as APIExceptions
from lib.settings import Settings
from lib.email_sender import EmailSender
from threading import Timer
from lib.util.logger import init_logger
from lib.util.hash import sha256
from lib.settings import Settings
from os import path, remove
from datetime import datetime
from lib.util.enums import SubscriptionTypes

class DatabaseDrivenObject:
    def __init__(self, file_name: str = 'database.db'):
        
        #Test if 'data' folder exists. If not, create it.
        directory = 'data'
        self.create_directory_if_not_exists(directory)

        #All database files will be located at data folder
        self.conn = sqlite3.connect(f'{directory}/{file_name}')
        self.cursor = self.conn.cursor()
        self.logger = init_logger(self.__class__.__name__)

    @staticmethod
    def create_directory_if_not_exists(directory):
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)

    def init_tables(self):
        script = 'lib/sql/init_tables.sql'
        self.logger.debug(f'Initializing database from `{script}` file...')

        #Load tables init sql request from 'lib/sql/init_tables.sql' and execute it. 
        request_file = open(script, mode='r')
        self.cursor.executescript(request_file.read())
        self.conn.commit()
