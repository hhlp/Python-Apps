import os
import sys
import string
import random
import sqlite3
import datetime
from argon2 import PasswordHasher
from cryptography.fernet import Fernet


class UserBank(object):
    def __init__(self, username, password):
        self.salt = None
        self.user_id = None
        self.created = None
        self.username = username
        self.password = self.password_hash(password)
        
    def __str__(self):
        return f"{self.username} {self.password} {self.salt}"
        
    def password_hash(self, password):
        password = Hashing(password).hash_password()
        password, self.salt = Salting(password).salt()
        return Hashing(password).hash_password()
    
    def user_object(self):
        database = Database()
        database.get_account(self.username)
        database.cursor.close()
        database.connection.close()
    
    def save_user(self):
        database = Database()
        database.save_account(self.username, self.password, self.salt)
        database.cursor.close()
        database.connection.close()

    
class MetaSingleton(type):
    """ Insures only a single connection to the database is available at the time. """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=MetaSingleton):
    connection = None
    def __init__(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.cursor, self.connection = self.connect()
        self.table_name = "Users"
        self.time = str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (user_id int, username TEXT, password TEXT, salt TEXT, created TEXT)")
        
    def connect(self):
        """ Makes sure to make a connection to the database, if no connection is active. """
        if self.connection is None:
            self.connection = sqlite3.connect("UserBank.db")
            self.cursor = self.connection.cursor()
        return self.cursor, self.connection
    
    def get_account(self, username):
        """ Fetches the account from the database. """
        self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE username = ?", (username,))
        print(self.cursor.fetchall())
    
    def save_account(self, username, password, salt):
        """ Saves the account to the database. """
        user_id = self.cursor.execute(f"SELECT MAX(user_id) FROM {self.table_name}").fetchone()[0] + 1
        created = self.time
        self.cursor.execute(f"INSERT INTO {self.table_name} (user_id, username, password, salt, created) VALUES(?,?,?,?,?)", (user_id, username, password, salt, created))
        self.connection.commit()
        print(f"Account {username} created successfully!")


class Hashing(object):
    def __init__(self, password):
        self.password = password
        self.hasher = PasswordHasher()
        
    def hash_password(self):
        """ Argon2 hash password """
        return self.hasher.hash(self.password)

    def verify_password(self, hashed_password):
        """ Compare new hashed password to old hashed password """
        return self.hasher.verify(self.hash_password(), hashed_password)


class Salting(object):
    def __init__(self, password):
        self.password = password
    
    def salt(self):
        """ Append salt to a hashed password """
        salt = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
        return self.password + salt, salt
    

if __name__ == "__main__":
    username = "Username"
    password = "Password"
    UserBank(username, password).save_user()
    