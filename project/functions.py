import string
import os
import json
import requests
import hashlib

from flask import request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from bs4 import BeautifulSoup

from project import db, app, models, ALLOWED_EXTENSIONS
from project.models import Products, Categories, Users, Files, USD_Rate

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def usd_sell_rate():
    with app.app_context():
        url = "http://www.udinform.com/"
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        usd_element = soup.find('td', string='USD')
        usd_buy_rate_el = usd_element.find_next_sibling('td')
        usd_sell_rate_el = usd_buy_rate_el.find_next_sibling('td')

        result = round(float(usd_sell_rate_el.text.strip()), 2)

        usd_rate_object = USD_Rate(
            usd_rate = round(float(result), 2)
        )
        db.session.add(usd_rate_object)
        db.session.commit()

        print("+")

        return round(float(result), 2)

def convert_to_uah(price):
    with app.app_context():
        last_row = USD_Rate.query.order_by(USD_Rate.id.desc()).first()

        usd_rate_today = float(last_row.usd_rate)

        finish_price = price * usd_rate_today

        return round(finish_price)      

def edit_json(path, chapter, key, text):
    if os.path.exists(path):
        with open(path, 'r') as f:
            json_data = json.load(f)
            json_data[chapter][key] = text

        with open(path, 'w') as f:
            f.write(json.dumps(json_data, indent = 4))


def add_product_to_cart(data, id, name, category_id, image, price, amount, finall_price):
    data.append({
        "id": id,
        "name": name,
        "category": category_id,
        "image": image,
        "price": price,
        "amount": amount,
        "finall_price": finall_price
    })

def check(data, id, name, category_id, image, price, amount, finall_price):
    for item in data:
        if item["id"] == id:
            item["amount"] += amount
            item["finall_price"] += int(convert_to_uah(item["price"])) * int(amount)
            return

    add_product_to_cart(data, id, name, category_id, image, price, amount, finall_price)

def set_signed_cookie(key, value):
    digest = hashlib.sha256(app.secret_key.encode("utf-8") + key.encode("utf-8") + value.encode("utf-8")).hexdigest()

    responsdsfasdfe = {
        "status": "redirect",
        "redirect": "/profile"
    }

    response = make_response(jsonify(responsdsfasdfe))
    response.set_cookie(key, value = value, max_age = app.config["COOKIE_LIFETIME"])
    response.set_cookie(key + "_sig", value = digest, max_age = app.config["COOKIE_LIFETIME"])

    return response

def get_signed_cookie(key):
    value = request.cookies.get(key)
    digest = request.cookies.get(key + "_sig")

    if value and digest:
        if hashlib.sha256(app.secret_key.encode("utf-8") + key.encode("utf-8") + value.encode("utf-8")).hexdigest() == digest:
            return value

    return None