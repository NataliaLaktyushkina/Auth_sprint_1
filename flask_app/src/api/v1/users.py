from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash

from app import app
from database.db import db
from database.dm_models import User


@app.route('/user', methods=['POST'])
def create_user(username, password):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(login=data['login'],
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created'})


@app.route('/user/<login>', methods=['DELETE'])
@jwt_required()
def delete_user(current_user: User, login: str):

    current_user = get_jwt_identity()
    if not current_user.admin:
        return jsonify({'message': 'Permission denied'})

    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({'message': 'No user found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User has been deleted'})


@app.route('/user/<login>', methods=['GET'])
def get_one_user(login: str):
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user_data = {'login': user.login,
                 'password': user.password,
                 'admin': user.admin}
    return jsonify({'user': user_data})


@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Display a list of users
    :return: list of users in json format
    """
    current_user = get_jwt_identity()
    if not current_user.admin:
        return jsonify({'message': 'Permission denied'})

    users = User.query.all()
    output = []
    for user in users:
        user_data = {'id': user.id,
                     'login': user.login,
                     'password': user.password,
                     'admin': user.admin}
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/user/<login>', methods=['PUT'])
@jwt_required()
def promote_user(login: str):
    current_user = get_jwt_identity()
    if not current_user.admin:
        return jsonify({'message': 'Permission denied'})
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promoted'})
