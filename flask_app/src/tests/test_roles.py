
from http import HTTPStatus


def test_create_role(client_with_db, access_headers, create_user):
    new_role = 'test_create_role'
    response = client_with_db.post('/v1/create_role',
                                   data={"new_role": new_role},
                                   headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_delete_role(client_with_db, create_role, access_headers):
    role = create_role.name
    response = client_with_db.delete('/v1/delete_role',
                                     data={"role": role},
                                     headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_change_role(client_with_db, create_role, access_headers):
    role = create_role.name
    new_name = 'test_change_role'
    response = client_with_db.put('/v1/change_role',
                                  data={"role": role,
                                        'new_name': new_name},
                                  headers=access_headers)
    assert response.status_code == HTTPStatus.OK


def test_roles_list(client_with_db, create_role, access_headers):
    response = client_with_db.get('/v1/roles_list',
                                  headers=access_headers)
    assert response.status_code == HTTPStatus.OK
