#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, request
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

class FileLink(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer(), primary_key=True)
    link = db.Column(db.String(50), nullable=False, unique=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.link)


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['name']
        password = request.form['pass']

        article = User(username=username, password_hash=password)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/create')

        except:
            return "Ошибка"
    else:
        return render_template("login.html")


@app.route('/create', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            # Функция secure_filename не дружит с не ascii-символами, поэтому
            # файлы русскими словами не называть
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Функция url_for('uploaded_file', filename=filename) возвращает строку вида: /uploads/<filename>
            link=url_for('uploaded_file', filename=filename)
            art=FileLink(link=link)
            try:
                db.session.add(art)
                db.session.commit()
                return redirect(url_for('uploaded_file', filename=filename))

            except:
                return "Ошибка"
                

    return render_template("index.html")


@app.route('/all')
def user():
    articles = User.query.all()
    return render_template("all.html", articles = articles)

# Пример обработчика, возвращающий файлы из папки app.config['UPLOAD_FOLDER'] для путей uploads и files.
# т.е. не нужно давать специальное название, чтобы получить файл в flask
# @app.route('/uploads/<filename>')
@app.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    # Localhost
    app.debug = True
    # Включение поддержки множества подключений
    app.run(threaded=True)