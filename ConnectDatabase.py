from mysql import connector
from mysql.connector import Error
import sys
import os


class ConnectDatabase(object):
    def __init__(self):
        self.user_name = os.environ.get("USER_NAME")
        self.password = os.environ.get("PASSWORD")
        self.server = os.environ.get("DATABASE_SERVER")
        self.database = os.environ.get("DATABASE")
        self.con = None
        self.cursor = None

    def connect_to_database(self):
        try:
            self.con = connector.connect(host=self.server,
                                         database=self.database,
                                         user=self.user_name,
                                         password=self.password)
        except Error:
            print("Unable to connect to database...")
            sys.exit(1)
        self.cursor = self.con.cursor()

    def close_connection_to_database(self):
        self.cursor.close()
        self.con.commit()
        self.con.close()

