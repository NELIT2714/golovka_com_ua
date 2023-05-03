from flask import Flask, render_template, redirect, url_for, session, json, make_response, request, jsonify

from project import app, db, models

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(405)
def page_not_found(e):
    return render_template("errors/404.html"), 405