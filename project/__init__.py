from flask import Flask, render_template, redirect, url_for, session, json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_apscheduler import APScheduler

import requests

app = Flask(__name__)
cron = APScheduler()

file = open("config.json", "r", encoding = "UTF-8")
config = json.load(file)

host = config["db"]["host"]
user = config["db"]["user"]
database = config["db"]["database"]
password = config["db"]["password"]
port = config["db"]["port"]

app.config["SECRET_KEY"] = config["web"]["secret-key"]
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{user}:{password}@{host}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["COOKIE_LIFETIME"] = 604800
app.config["UPLOAD_FOLDER"] = "project/static/users_images/"

ALLOWED_EXTENSIONS = ["png", "webp", "jpeg", "jpg", "svg"]

db = SQLAlchemy(app)

from project import routes, models, errors_handlers