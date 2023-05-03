from project import app, db
from datetime import datetime, timedelta

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable = False, unique = True)
    admin = db.Column(db.Boolean, nullable = False, default = False)
    password = db.Column(db.Text, nullable = False)
    reg_date = db.Column(db.DateTime, default = datetime.now)

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Products(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    short_description = db.Column(db.String(800), nullable = False)
    html_description = db.Column(db.Text, nullable = False)
    image = db.Column(db.String(100), nullable = False)
    date = db.Column(db.DateTime, default = datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Categories", backref=db.backref("products", lazy=True))

    def __init__(self, name, price, short_description, html_description, image, category):
        self.name = name
        self.price = price
        self.short_description = short_description
        self.html_description = html_description
        self.image = image
        self.category = category

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False, unique = True)
    image = db.Column(db.String(100), nullable = False)

    def __init__(self, name, image):
        self.name = name
        self.image = image

class Files(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    date = db.Column(db.DateTime, default = datetime.now)

    def __init__(self, name):
        self.name = name

class USD_Rate(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usd_rate = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime, default = datetime.now)

    def __init__(self, usd_rate):
        self.usd_rate = usd_rate