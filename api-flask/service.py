from db import get_db
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256 
from base64 import b64decode


def insert_order(beds, tables, chairs, armchairs, client_number, created_at, verify):

    db = get_db()
    cursor = db.cursor()
    statement = 'INSERT INTO orders(beds, tables, chairs, armchairs, client_number, created_at, verify) VALUES (?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(statement, [beds, tables, chairs, armchairs, client_number, created_at, verify])
    db.commit()

def get_public_key_by_client_number(client_number):

    db = get_db()
    cursor = db.cursor()
    statement = "SELECT public_key FROM employeers WHERE client_number = ?"
    cursor.execute(statement, [client_number])

    return cursor.fetchone()

def validate_order(order):

    res = True
    for key in order.keys():
        if order[key] < 0 | order[key] > 300:
            res = False
    
    return res

def verify_signature(order, signature, client_number):

    public_key_pem = get_public_key_by_client_number(client_number)
    public_key = RSA.PublicKey.load_pkcs1(public_key_pem.encode('utf8')) 
    signer = PKCS1_v1_5.new(public_key)
    digest = SHA256.new()
    digest.update(b64decode(order))

    return signer.verify(digest, b64decode(signature))

