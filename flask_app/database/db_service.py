from datetime import datetime

from werkzeug.security import generate_password_hash

from database.db import db
from .dm_models import User, LoginHistory, RefreshTokens


def get_user_by_login(login: str) -> User:
    user = User.query.filter_by(login=login).first()
    return user


def add_record_to_login_history(user: User, user_agent: str):
    # запись в БД попытки входа
    new_session = LoginHistory(user_id=user.id,
                               user_agent=user_agent,
                               auth_date=datetime.now())
    db.session.add(new_session)
    db.session.commit()


def add_refresh_token_to_db(user, refresh_token):
    # запись в БД refresh token
    new_record = RefreshTokens(user_id=user.id,
                               refresh_token=refresh_token)
    db.session.add(new_record)
    db.session.commit()

def create_user(username, password):
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(login=username,
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return new_user


def change_login(user: User, new_login: str):
    user.login = new_login
    db.session.commit()


def change_password(user: User, new_password: str):
    hashed_password = generate_password_hash(new_password, method='sha256')
    user.password = hashed_password
    db.session.commit()


