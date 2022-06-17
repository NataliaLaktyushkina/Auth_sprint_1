from flask import Flask
from flask_sqlalchemy import SQLAlchemy

username = 'app'
password = '123qwe'
host = '127.0.0.1:5432'
database_name ='movies_database'

db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}/{database_name}'
    db.init_app(app)

