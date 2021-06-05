from flask import Flask, jsonify, request
from service import insert_order, verify_signature, validate_order
from report import update_KPI
from db import create_tables
import ssl
from ratelimit import limits
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) 
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile = 'cert/server.crt', keyfile = 'cert/server.key')   
context.load_verify_locations(cafile='cert/client.pem')


@app.route('/order', methods = ['POST'])
@limits(calls = 3, period = 14400)
def post_order():

    order = request.get_json()['order']
    beds = order['beds']
    tables = order['tables']
    chairs = order['chairs']
    armchairs = order['armchairs']
    client_number = order['client_number']
    
    signature = request.get_json()['signature']
    
    verify = verify_signature(order, signature, client_number)
    
    valid = validate_order(order)

    insert_order(beds, tables, chairs, armchairs, client_number, datetime.now().strftime('%d/%m/%Y, %H:%M:%S'), verify)

    if verify & valid:

        return jsonify({'message': 'Petición OK'}), 200

    else:

        if verify == False:

            return jsonify({'message': 'Petición INCORRECTA'}), 403

        else:

            return jsonify({'message': 'Petición INCORRECTA'}), 400


if __name__ == '__main__':
    
    create_tables()

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(update_KPI, 'interval', weeks=8)
    sched.start()

    app.run(host = '127.0.0.1', port = 8081, debug = False, ssl_context=context)