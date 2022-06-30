from http import HTTPStatus
import base64


def test_login(client_with_db):
    credentials = base64.b64encode(b'first_user:12345').decode('utf-8')
    response = client_with_db.post('/v1/login', headers={
        'Authorization': 'Basic ' + credentials
    })
    assert response.status_code == HTTPStatus.OK.value


# def test_login_history(client_with_db):
#     # logging user
#     credentials = base64.b64encode(b'first_user:12345').decode('utf-8')
#     response = client_with_db.post('/v1/login', headers={
#         'Authorization': 'Basic ' + credentials
#     })
#     access_token = response.data['access_token']
#
#     headers={"X-Auth-Token": access_token}
#     response = client_with_db.get('/v1/login_history', headers=headers)
#     assert response.status_code == HTTPStatus.OK.value
#     assert len(response.data) == 1
#
#
# def test_singup(client_with_db):
#     username = 'test_user'
#     password = '12345'
#     response = client_with_db.post('/v1/sign_up', da
#     )


# def test_auth_token(app):
#     with app.test_request_context("/user/2/edit", headers={"X-Auth-Token": "1"}):
#         app.preprocess_request()
#         assert g.user.name == "Flask"



# app_v1_blueprint.add_url_rule('/change_login', methods=["POST"], view_func=change_login)
# app_v1_blueprint.add_url_rule('/change_password', methods=["POST"], view_func=change_password)
# app_v1_blueprint.add_url_rule('/logout', methods=["DELETE"], view_func=logout)
# app_v1_blueprint.add_url_rule('/refresh', methods=["GET"], view_func=refresh)
# app_v1_blueprint.add_url_rule('/sign_up', methods=["POST"], view_func=sign_up)
