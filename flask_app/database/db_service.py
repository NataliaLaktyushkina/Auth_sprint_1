from datetime import datetime

from database.db import db
from .dm_models import User, LoginHistory, RefreshTokens
from flask_jwt_extended import get_jwt


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

