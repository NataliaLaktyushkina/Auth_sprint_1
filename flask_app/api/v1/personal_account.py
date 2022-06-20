from datetime import timedelta

from flask import jsonify, request, make_response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.security import check_password_hash

from database.db_service import add_record_to_login_history, \
    add_refresh_token_to_db
from database.dm_models import User, LoginHistory, RefreshTokens
from database.redis_db import redis_app

ACCESS_EXPIRES = timedelta(hours=1)
REFRESH_EXPIRES = timedelta(days=30)

class Personal_Acc():

    def sign_up(self):
        """
        регистрация нового пользователя
        """
        # в запросе приходят логин и пароль
        # - проверяем, что такого пользователя в БД нет
        # - создаем нового пользователя
        # - отправляем access и refresh токены
        # - refresh-токены добавляем в psql с привязкой к пользователю


        return ''

    def login(self):
        """
        Вход пользователя в аккаунт:
        обмен логина и пароля на пару токенов:
        JWT-access токен и refresh токен);
        """
        auth = request.authorization

        if not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        user = User.query.filter_by(login=auth.username).first()
        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        if check_password_hash(user.password, auth.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            user_agent = request.headers['user_agent']

            # запись в БД попытки входа
            add_record_to_login_history(user, user_agent)

            # запись в БД refresh token
            add_refresh_token_to_storage(user, refresh_token)

            return jsonify(access_token=access_token,
                           refresh_token=refresh_token)

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # user’s refresh token must also be revoked when logging out;
    # otherwise, this refresh token could just be used to generate a new access token.
    @jwt_required(verify_type=False)
    def logout(self):
        # добавить user_agent
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        user_agent = request.headers['user_agent']
        redis_app.set(jti, "", ex=ACCESS_EXPIRES)

        # Returns "Access token revoked" or "Refresh token revoked"
        return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")

    # We are using the `refresh=True` options in jwt_required to only allow
    # refresh tokens to access this route.
    @jwt_required(refresh=True)
    def refresh(self):
        """
        выдаёт новую пару токенов (access и refresh) в обмен на корректный refresh-токен.
        """
        identity = get_jwt_identity() # user_id
        # Проверка, что пользователь тот же
        token = get_jwt()
        jti = token["jti"]
        user_db = RefreshTokens.query.filter_by(refresh_token=jti).first()
        if identity == user_db.user_id:
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            return jsonify(access_token=access_token,
                           refresh_token=refresh_token)

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    @jwt_required()
    def login_history(self):
        """
        получение пользователем своей истории входов в аккаунт
        """
        user_id = get_jwt_identity()

        history = LoginHistory.query.filter_by(user_id=user_id).\
            order_by(LoginHistory.auth_date.desc()).\
            limit(10)
        output = []
        for record in history:
            record_data = {'user_agent': record.user_agent,
                           'auth_date': record.auth_date}
            output.append(record_data)
        return jsonify(login_history=output)

    @jwt_required()
    def change_login(self):
        return ''

    @jwt_required()
    def change_password(self):
        return ''