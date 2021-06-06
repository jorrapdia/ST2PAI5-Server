import sqlite3


def get_db():
    conn = sqlite3.connect('hotel.db')
    return conn


def create_tables():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                                username TEXT PRIMARY KEY,
                                public_key TEXT UNIQUE);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders(
                                beds INTEGER,
                                tables INTEGER,
                                chairs INTEGER,
                                armchairs INTEGER,
                                order_date TIMESTAMP,
                                user_id TEXT,
                                FOREIGN KEY(user_id) REFERENCES users(username));''')
    db.commit()


def insert_order(beds, tables, chairs, armchairs, order_date, user_id):
    db = get_db()
    cursor = db.cursor()
    statement = 'INSERT INTO orders(beds, tables, chairs, armchairs, order_date, user_id) VALUES(?, ?, ?, ?, ?, ?)'
    cursor.execute(statement, [beds, tables, chairs, armchairs, order_date, user_id])
    db.commit()


def get_public_key_by_client_number(client_number):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT public_key FROM users WHERE username = ?"
    cursor.execute(statement, [client_number])
    res = cursor.fetchone()
    if res is not None:
        res = res[0]
    return res


def insert_user(username, public_key):
    try:
        connection = get_db()
        connection.cursor().execute(
            'INSERT INTO users(username, public_key) VALUES(?, ?)', [username, public_key])
        connection.commit()
        print("INFO: User inserted in database.")
    finally:
        connection.close()
