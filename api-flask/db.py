import sqlite3

def get_db():

    conn = sqlite3.connect('hotel.db')

    return conn


def create_tables():

    tables = [
        '''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                beds INTEGER, 
                                                tables INTEGER, 
                                                chairs INTEGER, 
                                                armchairs INTEGER, 
                                                client_number INTEGER,
                                                created_at TEXT,
                                                verify BOOLEAN NOT NULL CHECK (verify IN (True, False)))''', 
        '''CREATE TABLE IF NOT EXISTS employeers (client_number INTEGER PRIMARY KEY, 
                                                public_key TEXT UNIQUE)'''
    ]

    db = get_db()
    cursor = db.cursor()
    
    for table in tables:
        cursor.execute(table)