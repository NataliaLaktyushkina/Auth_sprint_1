import pytest
import sys, os
sys.path.append(os.path.dirname(__file__) + '/..')
# from auth_app import app
from auth_app import  create_app

# from auth_app import app
from dataclasses import dataclass
from utils import settings
from typing import Optional

from flask_sqlalchemy import SQLAlchemy

from utils import settings

db_settings = settings.get_settings()

username = db_settings.USERNAME
password = db_settings.PASSWORD
# host = db_settings.HOST
# port = db_settings.PORT
host = '127.0.0.1'
port = '5433'
host_port = ':'.join((host, port))
database_name = db_settings.DATABASE_NAME

db = SQLAlchemy()


@pytest.fixture()
def app():
    # other setup can go her
    app = create_app()

    app.config.update({
        'SQLALCHEMY_DATABASE_URI' : f'postgresql://{username}:{password}@{host_port}/{database_name}'})
    app.config.update({
        "TESTING": True,
    })
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    yield app

    # clean up / reset resources here

#
# @pytest.fixture()
# def client(app):
#     return app.test_client()


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def client_with_db(app_with_db):
    return app_with_db.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def app_with_db(app):
    # db = SQLAlchemy(app)
    db.init_app(app)
    app.app_context().push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
