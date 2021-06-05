import socket
import ssl
import _thread
import logging
import db

from service import verify_signature
from datetime import datetime


def is_valid_user(username, public_key):
    res = True
    public_key_db = db.get_public_key_by_client_number(username)
    if public_key_db is None:
        db.insert_user(username, public_key)
    else:
        res = public_key_db == public_key
    return res


def threaded_client(connection):
    while True:
        data = connection.recv(2048)
        if not data:
            continue
        received_info = str(data, 'utf-8')
        received_info_sp = received_info.split(';')
        if len(received_info_sp) == 3:
            message_sp = received_info_sp[0].strip().split(" ")
            if len(message_sp) == 5 and is_valid_user(message_sp[4].strip(),
                                                      received_info_sp[1].strip()) and verify_signature(
                    received_info_sp[0].strip(), received_info_sp[2].strip(), received_info_sp[1].strip()):
                db.insert_order(message_sp[0].strip(), message_sp[1].strip(), message_sp[2].strip(),
                                message_sp[3].strip(), datetime.now().timestamp(), message_sp[4].strip())
                print(
                    '{Username: ' + received_info_sp[0].strip() + ', Message: ' + received_info_sp[2].strip() + '}')
                connection.sendall(bytes('Message saved successfully\r\n', 'utf-8'))
            else:
                print('The message has been discarded due to an error in the format')
                connection.sendall(bytes('The message has been discarded due to an error in the format\r\n', 'utf-8'))
        else:
            print('The message has been discarded due to an error in the format')
            connection.sendall(bytes('The message has been discarded due to an error in the format\r\n', 'utf-8'))
        break


def tls13_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_verify_locations(cafile='certs/client.crt')
    context.load_cert_chain(keyfile='certs/server.key', certfile='certs/server.crt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('192.168.1.10', 8443))
        s.listen(1)
        print('Server up, waiting for a connection')
        with context.wrap_socket(s, server_side=True) as ssock:
            while True:
                connection, a = ssock.accept()
                logging.info('Received connection from ' + str(a))
                _thread.start_new_thread(threaded_client, (connection,))
                logging.info('Closing connection')


if __name__ == '__main__':
    db.create_tables()
    tls13_server()
