import base64
import os
import sys

import pytest

sys.path.append(os.path.dirname(__file__) + '/..')
from auth_app import  create_app

from flask_sqlalchemy import SQLAlchemy

from utils import settings
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID


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


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<User {self.login}>'


class LoginHistory(db.Model):
    __tablename__ = 'login_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey(User.id))
    user_agent = db.Column(db.String, nullable=False)
    auth_date = db.Column(db.DateTime, nullable=False)


class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Roles {self.name}>'


class UsersRoles(db.Model):
    """связь пользователя и роли.
    Одному пользователю может быть назначено несколько ролей """
    __tablename__ = 'users_roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey(User.id))
    role_id = db.Column(UUID(as_uuid=True), ForeignKey(Roles.id))


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


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def app_with_db(app):
    db.init_app(app)
    app.app_context().push()
    db.create_all()

    yield app
    db.drop_all()
    db.session.remove()


@pytest.fixture()
def client_with_db(app_with_db):
    return app_with_db.test_client()


@pytest.fixture()
def create_role():
    test_role = Roles(name='test_role')
    db.session.add(test_role)
    db.session.commit()

    return test_role

@pytest.fixture()
def create_user():
    test_user = User(login='test_admin', password='12345')
    db.session.add(test_user)
    admin_role = Roles(name='admin')
    db.session.add(admin_role)
    db.session.commit()
    new_assignment = UsersRoles(user_id=test_user.id,
                                role_id=admin_role.id)
    db.session.add(new_assignment)
    db.session.commit()

    return test_user


@pytest.fixture()
def token_response(create_user,  client_with_db):
    user = create_user.login
    password = create_user.password
    my_str = ':'.join((user, password)).encode('utf-8')
    credentials = base64.b64encode(my_str).decode('utf-8')
    response = client_with_db.post('/v1/login', headers={
        'Authorization': 'Basic ' + credentials
    })
    return response

@pytest.fixture()
def access_headers(token_response):

    access_token = token_response.json.get('access_token')
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    return headers


@pytest.fixture()
def refresh_headers(token_response):
    refresh_token = token_response.json.get('refresh_token')
    headers = {
        'Authorization': 'Bearer ' + refresh_token
    }
    return headers

