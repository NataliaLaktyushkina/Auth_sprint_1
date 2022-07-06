from http import HTTPStatus
import base64


def test_login(client_with_db, create_user):
    username = create_user.login
    password = create_user.password
    my_str = ':'.join((username, password)).encode('utf-8')
    credentials = base64.b64encode(my_str).decode('utf-8')
    response = client_with_db.post('/v1/login', headers={
        'Authorization': 'Basic ' + credentials
    })
    assert response.status_code == HTTPStatus.OK


def test_login_history(client_with_db, access_headers):
    response = client_with_db.get('/v1/login_history', headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_singup(client_with_db):
    username = 'test_user7'
    password = '12345'
    response = client_with_db.post('/v1/sign_up',
                                   data={'username': username,
                                         'password': password}
                                   )
    assert response.status_code == HTTPStatus.OK


def test_change_login(client_with_db, access_headers):
    new_username = 'test_user_change_login'
    response = client_with_db.post('/v1/change_login',
                                   data={"new_username": new_username},
                                   headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_change_password(client_with_db, access_headers):
    new_password = 'test_change_pass'
    response = client_with_db.post('/v1/change_password',
                                   data={'new_password': new_password},
                                   headers=access_headers
                                   )
    assert response.status_code == HTTPStatus.OK


def test_logout(client_with_db, access_headers):
    response = client_with_db.delete('/v1/logout',
                                     headers=access_headers
                                     )
    assert response.status_code == HTTPStatus.OK


def test_refresh(client_with_db, refresh_headers):
    response = client_with_db.get('/v1/refresh',
                                  headers=refresh_headers
                                  )
    assert response.status_code == HTTPStatus.OK
