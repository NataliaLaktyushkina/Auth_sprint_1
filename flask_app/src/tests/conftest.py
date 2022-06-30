import pytest
import sys, os
sys.path.append(os.path.dirname(__file__) + '/..')
# from auth_app import app
from auth_app import  create_app

# from auth_app import app
from dataclasses import dataclass
from utils import settings
from typing import Optional

#
# app_settings = settings.get_settings()
#
# @dataclass
# class HTTPResponse:
#     body: dict
#     headers: [str]
#     status: int
#
# @pytest.fixture(scope='session')
# def redis_client():
#     client =  aioredis.create_redis_pool((app_settings.REDIS_HOST, app_settings.REDIS_PORT), minsize=10, maxsize=20)
#     # Clean cache
#     client.flushall()
#     yield client
#     await client.wait_closed()
# #
# @pytest.fixture
# def make_get_request(session):
#     async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
#         params = params or {}
#         url = app_settings.URL_API_V1 + method
#         async with session.get(url, params=params) as response:
#             return HTTPResponse(
#                 body=await response.json(),
#                 headers=response.headers,
#                 status=response.status,
#             )
#
#     return inner

from flask_sqlalchemy import SQLAlchemy

from utils import settings

db_settings = settings.get_settings()

username = db_settings.USERNAME
password = db_settings.PASSWORD
host = db_settings.HOST
port = db_settings.PORT
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
    db.init_app(app)
    app.app_context().push()
    db.create_all()

    yield app

    db.session.commit()
    db.drop_all()