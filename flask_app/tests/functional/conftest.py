from datetime import timedelta

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from utils import settings

db_settings = settings.get_settings()

ACCESS_EXPIRES = timedelta(hours=1)
REFRESH_EXPIRES = timedelta(days=30)
username = db_settings.USERNAME
password = db_settings.PASSWORD
host = db_settings.HOST
port = db_settings.PORT
host_port = ':'.join((host, port))
database_name = db_settings.DATABASE_NAME

app_settings = settings.get_settings()

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = settings.get_settings().SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_EXPIRES


    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host_port}/{database_name}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.app = app
    db.init_app(app)

    # app.register_blueprint('/login')
    return app


@pytest.fixture
def flask_app():
    app = create_app()

    client = app.test_client()

    ctx = app.test_request_context()
    ctx.push()

    yield client

    ctx.pop()


@pytest.fixture
def app_with_db(flask_app):
    db.create_all()

    yield flask_app

    db.session.commit()
    db.drop_all()



