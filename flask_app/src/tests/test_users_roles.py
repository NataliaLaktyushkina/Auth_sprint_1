from http import HTTPStatus


def test_users_roles(client_with_db, access_headers, create_user):
    username = create_user.login
    response = client_with_db.get('/v1/users_roles',
                                  json={"username": username},
                                  headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_assign_role(client_with_db, access_headers,
                     create_user, create_role):
    username = create_user.login
    role = create_role.name
    response = client_with_db.post('/v1/assign_role',
                                   json={"username": username,
                                         'role': role},
                                   headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_detach_role(client_with_db, access_headers,
                     create_user, create_role):
    username = create_user.login
    role = create_role.name
    response = client_with_db.delete('/v1/detach_role',
                                   json={"username": username,
                                         'role': role},
                                   headers=access_headers)
    assert response.status_code == HTTPStatus.OK
