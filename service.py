from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512
from datetime import datetime
from datetime import timedelta

import config
import db as database
import dateutil.relativedelta

i = 0
c = config.Config()


def validate_order(quantities):
    res = True
    for quantity in quantities:
        if int(quantity) < 0 or int(quantity) > 300:
            res = False
    return res


def verify_user(username, public_key):
    res = True
    public_key_db = database.get_public_key_by_client_number(username)
    if public_key_db is None:
        database.insert_user(username, public_key)
    else:
        res = public_key_db == public_key
    return res


def verify_signature(order, signature, public_key_pem):
    public_key = RSA.import_key(bytearray.fromhex(public_key_pem))
    signer = PKCS1_v1_5.new(public_key)
    digest = SHA512.new()
    digest.update(order.encode())
    return signer.verify(digest, bytearray.fromhex(signature))


def kpi():
    global i
    db = database.get_db()
    cursor = db.cursor()
    now = datetime.now()

    orders_last_month_query = "SELECT valid FROM orders WHERE (order_date >= " + str(
        (now - get_timedelta(1)).timestamp()) + " AND order_date <= " + str(
        now.timestamp()) + ")"
    orders_previous_month_query = "SELECT valid FROM orders WHERE (order_date >= " + str(
        (now - get_timedelta(2)).timestamp()) + " AND order_date <= " + str(
        (now - get_timedelta(1)).timestamp()) + ")"
    orders_previous_previous_month_query = "SELECT valid FROM orders WHERE (order_date >= " + str(
        (now - get_timedelta(3)).timestamp()) + " AND order_date <= " + str(
        (now - get_timedelta(2)).timestamp()) + ")"

    orders_last_month = cursor.execute(orders_last_month_query).fetchall()
    orders_previous_month = cursor.execute(orders_previous_month_query).fetchall()
    orders_previous_previous_month = cursor.execute(orders_previous_previous_month_query).fetchall()

    p3_ratio = len(list(filter(lambda x: x[0] > 0, orders_last_month))) / len(orders_last_month) if len(
        orders_last_month) > 0 else 0
    p2_ratio = len(list(filter(lambda x: x[0] > 0, orders_previous_month))) / len(orders_previous_month) if len(
        orders_previous_month) > 0 else 0
    p1_ratio = len(list(filter(lambda x: x[0] > 0, orders_previous_previous_month))) / len(orders_previous_previous_month) if len(
        orders_previous_previous_month) > 0 else 0

    if i > 1 and ((p3_ratio > p1_ratio and p3_ratio > p2_ratio) or (p3_ratio > p1_ratio and p3_ratio == p2_ratio) or (
            p3_ratio == p1_ratio and p3_ratio > p2_ratio)):
        tendencia = '+'
    elif i > 1 and (p3_ratio < p1_ratio or p3_ratio < p2_ratio):
        tendencia = '-'
    else:
        tendencia = '0'
        i += 1

    return p3_ratio, tendencia


def get_timedelta(time_amount):
    return timedelta(minutes=time_amount) if c.test else dateutil.relativedelta.relativedelta(months=time_amount)


def update_kpi():
    if c.test or datetime.now().day == 1:
        f = open("kpi.txt", "a+")
        ratio, tendencia = kpi()
        f.write(
            "Fecha: " + datetime.now().strftime("%B (%Y)") + " - Ratio: " + str(
                ratio) + " - Tendencia: " + tendencia + "\n")
        f.close()

        print('SERVER INFO: KPI was updated')
