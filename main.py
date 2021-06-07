import os
import random
import socket
import ssl
import _thread

import db
import schedule
import time

from service import *
from datetime import datetime

ERROR_MSG = "Peticion INCORRECTA"
c = config.Config()


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

            if c.test and random.randint(0, 1) > 0:
                order = "fail"

            user_is_valid = verify_user(client_number, public_key)
            sign_is_valid = verify_signature(order, signature, public_key)
            order_is_valid = validate_order([beds_number, tables_number, chairs_number, armchairs_number])
            if user_is_valid and sign_is_valid and order_is_valid:
                db.insert_order(beds_number, tables_number, chairs_number, armchairs_number, datetime.now().timestamp(),
                                client_number, 1)
                print('INFO: Petición correcta {Firma: ' + signature + ', Petición: ' + order + '}')
                connection.sendall(bytes('Peticion OK\r\n', 'utf-8'))
            else:
                db.insert_order(beds_number, tables_number, chairs_number, armchairs_number, datetime.now().timestamp(),
                                client_number, 0)
                print('INFO: ' + ERROR_MSG)
                connection.sendall(bytes(ERROR_MSG + '\r\n', 'utf-8'))
        else:
            db.insert_order(None, None, None, None, datetime.now().timestamp(), None, 0)
            print('INFO: ' + ERROR_MSG)
            connection.sendall(bytes(ERROR_MSG + '\r\n', 'utf-8'))
        break


def tls13_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_verify_locations(cafile='certs/client.crt')
    context.load_cert_chain(keyfile='certs/server.key', certfile='certs/server.crt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((c.server, c.port))
        s.listen(1)
        print('INFO: Servidor activo, esperando conexión')
        with context.wrap_socket(s, server_side=True) as ssock:
            while True:
                connection, a = ssock.accept()
                print('INFO: Conexión recibida: ' + str(a))
                _thread.start_new_thread(threaded_client, (connection,))
                print('INFO: Cerrando conexión')


def call_kpi():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    if os.path.exists("kpi.txt"):
        os.remove("kpi.txt")
    db.create_tables()
    if c.test:
        schedule.every(1).minutes.do(update_kpi)
    else:
        schedule.every().day.at("08:00").do(update_kpi)
    _thread.start_new_thread(call_kpi, ())
    tls13_server()

