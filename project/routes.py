import string
import os
import json

from flask import Flask, render_template, redirect, url_for, session, json, make_response, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from transliterate import translit
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from project import app, db, models, ALLOWED_EXTENSIONS
from project.models import Products, Categories, Users, Files
from project.functions import allowed_file, convert_to_uah, check, set_signed_cookie, get_signed_cookie

from project.fondy import checkout

@app.route("/index/")
@app.route("/home/")
@app.route("/main/")
@app.route("/")
def index():
    categories = Categories.query.all()
    return render_template("index.html", categories = categories)

@app.route("/profile/")
def profile():
    if not get_signed_cookie("golovka_email"):
        return redirect(url_for("sign_in"))

    categories = Categories.query.all()
    user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

    return render_template("profile/profile.html", categories = categories, user = user)

@app.route("/catalog/<int:category_id>/")
def category(category_id):
    category = Categories.query.filter_by(id = category_id).first()

    if not category:
        return abort(404)

    products = category.products
        
    return render_template("products.html", category = category, products = products, convert_to_uah = convert_to_uah)

@app.route("/catalog/<int:category_id>/product/<int:product_id>/")
def product_details(category_id, product_id):
    category = Categories.query.filter_by(id = category_id).first()
    product = Products.query.filter_by(id = product_id).first()

    if not category or not product:
        return abort(404)

    return render_template("product_details.html", product = product, category = category, convert_to_uah = convert_to_uah)

@app.route("/sign-up/", methods = ["GET", "POST"])
def sign_up():
    if get_signed_cookie("golovka_email"):
        return redirect(url_for("sign_in"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if Users.query.filter_by(email = email).all() == []:
            if 6 <= len(password) < 32:
                # uppercase = any([1 if i in string.ascii_uppercase else 0 for i in password])
                # lowercase = any([1 if i in string.ascii_lowercase else 0 for i in password])
                # digits = any([1 if i in string.digits else 0 for i in password])

                # characters = [uppercase, lowercase, digits]

                if password == confirm_password:
                    try:
                        user_object = Users(email = email, password = generate_password_hash(password = password, method = "md5", salt_length = 50))
                        db.session.add(user_object)
                        db.session.commit()

                        resp = set_signed_cookie("golovka_email", email)

                        return resp
                    except:
                        response = {
                            "status": "error",
                            "message": "Помилка при створенні облікового запису"
                        }
                        return jsonify(response)
                else:
                    response = {
                        "status": "error",
                        "message": "Паролі не однакові!"
                    }
                    return jsonify(response)
            else:
                response = {
                    "status": "error",
                    "message": "Пароль повинен бути не меньше 5ти і не більше 32х символів"
                }
                return jsonify(response)
        else:
            response = {
                "status": "error",
                "message": "Такий email вже занятий"
            }
            return jsonify(response)

    return render_template("profile/sign-up.html")

@app.route("/sign-in/", methods = ["GET", "POST"])
def sign_in():
    if get_signed_cookie("golovka_email"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not Users.query.filter_by(email = email).all() == []:
            user = Users.query.filter_by(email = email).first()

            if check_password_hash(user.password, password):
                resp = set_signed_cookie("golovka_email", email)

                return resp
            else:
                response = {
                    "status": "error",
                    "message": "Пароль введено неправильно"
                }
                return jsonify(response)
        else:
            response = {
                "status": "error",
                "message": "Акаунт не знайдено"
            }
            return jsonify(response)

    return render_template("profile/sign-in.html")

@app.route("/logout/")
def logout():
    if get_signed_cookie("golovka_email"):
        resp = make_response(redirect(url_for("index")))
        resp.delete_cookie("golovka_email")
        resp.delete_cookie("golovka_email_sig")
        return resp
    else:
        return redirect(url_for("index"))

# Cart

@app.route("/cart/")
def cart():
    cart_str = request.cookies.get("golovka_cart")
    cart_list = json.loads(cart_str)

    total_price = 0
    total_amount = 0

    for el in cart_list:
        total_price += convert_to_uah(int(el["price"])) * int(el["amount"])
        total_amount += int(el["amount"])

    return render_template("cart.html", cart = cart_list, enumerate = enumerate, convert_to_uah = convert_to_uah, len = len, total_price = total_price, total_amount = total_amount)

@app.route("/update-cart/", methods = ["POST"])
def update_cart():
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        amount = int(request.form["amount"])
        cart_str = request.cookies.get("golovka_cart")
        cart_list = json.loads(cart_str)

        product = Products.query.filter_by(id = product_id).first()

        for elt in cart_list:
            if elt["id"] == product_id:
                elt["amount"] = amount
                elt["finall_price"] = convert_to_uah(int(elt["price"])) * amount
                break

        total_price = sum([int(el["finall_price"]) for el in cart_list])
        total_amount = 0

        for el in cart_list:
            total_amount += int(el["amount"])

        resp = make_response(jsonify({
            "status": "success",
            "message": "Количество товара в корзине обновлено!",
            "finall_price": "{0:,}".format(int(convert_to_uah(product.price)) * amount).replace(',', ' '),
            "total_price": "{0:,}".format(total_price).replace(',', ' '),
            "total_amount": total_amount
        }))
        expires = datetime.utcnow() + timedelta(days=3650)
        cart_bytes = json.dumps(cart_list, ensure_ascii=False).encode("utf-8")
        resp.set_cookie("golovka_cart", cart_bytes, expires=expires)

        return resp

@app.route("/add-to-cart/", methods = ["POST"])
def add_to_cart():
    if request.method == "POST":
        product = Products.query.filter_by(id = int(request.form["product_id"])).first()

        if not product:
            return abort(404)

        amount = int(request.form["amount"])

        cart = request.cookies.get("golovka_cart")

        if not cart:
            cart = []
        else:
            cart = json.loads(cart)

        finall_price = convert_to_uah(product.price) * int(amount)
        check(cart, product.id, product.name, product.category_id, product.image, product.price, amount, finall_price)

        resp = make_response(jsonify({
            "status": "success",
            "message": "Продукт додано до кошика!"
        }))
        expires = datetime.utcnow() + timedelta(days=3650)
        cart_bytes = json.dumps(cart, ensure_ascii=False).encode("utf-8")
        resp.set_cookie("golovka_cart", cart_bytes, expires = expires)
        
        return resp

@app.route("/remove-from-cart/", methods = ["POST"])
def remove_from_cart():
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        cart_str = request.cookies.get("golovka_cart")
        cart_list = json.loads(cart_str)

        for i, elt in enumerate(cart_list):
            if elt["id"] == product_id:
                del(cart_list[i])
                break

        total_price = sum([int(el["finall_price"]) for el in cart_list])
        total_amount = 0

        for el in cart_list:
            total_amount += int(el["amount"])

        resp = make_response(jsonify({
            "status": "success",
            "message": "Продукт видалено з кошика",
            "cart_html": render_template("cart.html", cart = cart_list, enumerate = enumerate, convert_to_uah = convert_to_uah, len = len, total_price = total_price, total_amount = total_amount),
            "total_price": total_price
        }))
        expires = datetime.utcnow() + timedelta(days=3650)
        cart_bytes = json.dumps(cart_list, ensure_ascii=False).encode("utf-8")
        resp.set_cookie("golovka_cart", cart_bytes, expires=expires)

        return resp
    
@app.route("/clear-cart/")
def clear_cart():
    resp = make_response(jsonify({
        "status": "success",
        "message": "Всі продукти з кошика видалені"
    }))
    resp.delete_cookie("golovka_cart")
    return resp

# Ordering

@app.route("/ordering/")
def ordering():
    cart_str = request.cookies.get("golovka_cart")
    cart_list = json.loads(cart_str)

    total_price = 0
    total_amount = 0

    for el in cart_list:
        total_price += convert_to_uah(int(el["price"])) * int(el["amount"])
        total_amount += int(el["amount"])
    
    return render_template("ordering.html", cart = cart_list, total_amount = total_amount, total_price = total_price)

# Profile

@app.route("/main-info/", methods = ["POST"])
def main_info():
    if not get_signed_cookie("golovka_email"):
        return render_template("errors/not-auth.html")

    user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

    return render_template("profile/main-info.html", user = user)

@app.route("/change-password/", methods = ["POST"])
def change_password():
    if not get_signed_cookie("golovka_email"):
        return render_template("errors/not-auth.html")

    user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

    return render_template("profile/change-password.html", user = user)

# admin

@app.route("/admin/", methods = ["POST", "GET"])
def admin():
    if not get_signed_cookie("golovka_email"):
        return abort(404)

    user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

    if not user.admin:
        return abort(404)

    products = db.session.query(Products, Categories.name)\
        .join(Categories, Products.category_id==Categories.id)\
        .options(joinedload(Products.category))\
        .all()

    categories = Categories.query.all()

    return render_template("admin/admin.html", products = products, user = user, categories = categories, len = len)

@app.route("/add-category/", methods = ["GET", "POST"])
def add_category():
    if not request.cookies.get("golovka_email"):
        response = {
            "status": "redirect",
            "redirect": "/sign-in"
        }
        return jsonify(response)
    
    if request.method == "POST":
        category_name = request.form["category-name"]
        category_image = request.files["category-image"]

        if Categories.query.filter_by(name = category_name).all() == []:
            if category_image and allowed_file(category_image.filename):
                lastRow = Files.query.order_by(Files.id.desc()).first()
                fileName = category_image.filename

                if lastRow != None:
                    fileName = f"file_{lastRow.id + 1}.png"
                else:
                    fileName = f"file_1.png"

                category_image.save(os.path.join(app.config["UPLOAD_FOLDER"], fileName))

                file_object = Files(
                    name = fileName
                )

                category_object = Categories(
                    name = category_name,
                    image = fileName
                )

                db.session.add(category_object)
                db.session.add(file_object)
                db.session.commit()

                products = db.session.query(Products, Categories.name)\
                    .join(Categories, Products.category_id==Categories.id)\
                    .options(joinedload(Products.category))\
                    .all()

                categories = Categories.query.all()
                user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

                response = {
                    "status": "success",
                    "message": "Категорія була додана до списку категорій",
                    "html": render_template("admin/admin.html", products = products, user = user, categories = categories, len = len)
                }

                return jsonify(response)
            else:
                response = {
                    "status": "error",
                    "message": f"Розширення файлу повинно бути: {ALLOWED_EXTENSIONS}"
                }

                return jsonify(response)
        else:
            response = {
                "status": "error",
                "message": "Категорія з таким ім'ям вже є"
            }

            return jsonify(response)

@app.route("/add-product/", methods = ["GET", "POST"])
def add_product():
    if not request.cookies.get("golovka_email"):
        response = {
            "status": "redirect",
            "redirect": "/sign-in"
        }
        return jsonify(response)
    
    if request.method == "POST":
        product_name = request.form["name"]
        product_price = request.form["price"]
        product_category = request.form["category"]
        product_image = request.files["product-image"]
        product_short_desc = request.form["short-description"]
        product_html_desc = request.form["html-description"]

        category = Categories.query.get(product_category)
        if not category:
            return abort(404)

        if product_image and allowed_file(product_image.filename):
            lastRow = Files.query.order_by(Files.id.desc()).first()
            fileName = product_image.filename

            if lastRow != None:
                fileName = f"file_{lastRow.id + 1}.png"
            else:
                fileName = f"file_1.png"

            product_image.save(os.path.join(app.config["UPLOAD_FOLDER"], fileName))
            
            file_object = Files(
                name = fileName
            )

            if len(product_short_desc) > 800:
                response = {
                    "status": "error",
                    "message": "Короткий опис продукту не може бути більшим ніж 800 символів!"
                }

                return jsonify(response)
            else:
                new_html_desc = product_html_desc.replace("\n", "<br>")

                print(new_html_desc)
                
                product_object = Products(
                    name = product_name,
                    price = int(product_price),
                    short_description = product_short_desc,
                    html_description = new_html_desc,
                    image = fileName,
                    category = category
                )

                db.session.add(product_object)
                db.session.add(file_object)
                db.session.commit()

                products = db.session.query(Products, Categories.name)\
                    .join(Categories, Products.category_id==Categories.id)\
                    .options(joinedload(Products.category))\
                    .all()

                categories = Categories.query.all()
                user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

                response = {
                    "status": "success",
                    "message": "Продукт доданий до категорії",
                    "html": render_template("admin/admin.html", products = products, user = user, categories = categories, len = len)
                }

                return jsonify(response)
        else:
            response = {
                "status": "error",
                "message": f"Розширення файлу повинно бути: {ALLOWED_EXTENSIONS}"
            }

            return jsonify(response)

@app.route("/remove-category/<int:id>/", methods = ["POST"])
def remove_category(id):
    if not get_signed_cookie("golovka_email"):
        return abort(404)

    user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

    if not user.admin:
        return abort(404)

    if Products.query.filter_by(category_id = id).all() == []:
        try:
            category = Categories.query.get(id)
            db.session.delete(category)
            db.session.commit()

            products = db.session.query(Products, Categories.name)\
                    .join(Categories, Products.category_id==Categories.id)\
                    .options(joinedload(Products.category))\
                    .all()

            categories = Categories.query.all()

            return jsonify({
                "status": "success",
                "message": "Ви успішно видалили категорію",
                "html": render_template("admin/admin.html", products = products, user = user, categories = categories, len = len)
            })
        except:
            return jsonify({
                "status": "error",
                "message": "Виникла помилка при видалені категорії"
            })
    else:
        return jsonify({
            "status": "error",
            "message": "Спочатку видаліть всі продукти з категорії"
        })

@app.route("/remove-product/<int:id>/", methods = ["POST"])
def remove_product(id):
    if not get_signed_cookie("golovka_email"):
        return abort(404)

    user = Users.query.filter_by(email = get_signed_cookie("golovka_email")).first()

    if not user.admin:
        return abort(404)

    try:
        product = Products.query.get(id)
        db.session.delete(product)
        db.session.commit()

        products = db.session.query(Products, Categories.name)\
                .join(Categories, Products.category_id==Categories.id)\
                .options(joinedload(Products.category))\
                .all()

        categories = Categories.query.all()

        return jsonify({
            "status": "success",
            "message": "Продукт видалено",
            "html": render_template("admin/admin.html", products = products, user = user, categories = categories, len = len)
        })
    except:
        return jsonify({
            "status": "error",
            "message": "Виникла помилка при видалені продукту"
        })

# Потом удалить

@app.route("/db/")
def db_reset():
    db.drop_all()
    db.create_all()
    return redirect(url_for("index"))