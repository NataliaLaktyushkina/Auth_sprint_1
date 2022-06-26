import base64
from http import HTTPStatus


def test_login(app_with_data):
    valid_credentials = base64.b64encode(b"first_user:12345").decode("utf-8")
    headers = {"Authorization": "Basic " + valid_credentials}
    with app_with_data as c:
        response = c.post('/login', headers=headers)
        assert response.status_code == HTTPStatus.OK
