import socket
import ssl
import _thread
import logging
import db

from service import *
from datetime import datetime

ERROR_MSG = "El mensaje ha sido descartado por un error en su formato"


def threaded_client(connection):
    while True:
        data = connection.recv(10048)
        if not data:
            continue
        received_info = str(data, 'utf-8')
        received_info_sp = received_info.split(';')
        order = received_info_sp[0].strip()
        order_data = order.split(" ")
        if len(received_info_sp) == 3 and len(order_data) == 5:
            public_key = received_info_sp[1].strip()
            signature = received_info_sp[2].strip()
            beds_number = order_data[0].strip()
            tables_number = order_data[1].strip()
            chairs_number = order_data[2].strip()
            armchairs_number = order_data[3].strip()
            client_number = order_data[4].strip()

            user_is_valid = verify_user(client_number, public_key)
            sign_is_valid = verify_signature(order, signature, public_key)
            order_is_valid = validate_order([beds_number, tables_number, chairs_number, armchairs_number])
            if user_is_valid and sign_is_valid and order_is_valid:
                db.insert_order(beds_number, tables_number, chairs_number, armchairs_number, datetime.now().timestamp(),
                                client_number)
                print('{Signature: ' + signature + ', Order: ' + order + '}')
                connection.sendall(bytes('Pedido realizado correctamente\r\n', 'utf-8'))
            else:
                print(ERROR_MSG)
                connection.sendall(bytes(ERROR_MSG + '\r\n', 'utf-8'))
        else:
            print(ERROR_MSG)
            connection.sendall(bytes(ERROR_MSG + '\r\n', 'utf-8'))
        break


def tls13_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_verify_locations(cafile='certs/client.crt')
    context.load_cert_chain(keyfile='certs/server.key', certfile='certs/server.crt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('192.168.100.5', 8443))
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
