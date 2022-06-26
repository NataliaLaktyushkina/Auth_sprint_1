from http import HTTPStatus
import base64

import pytest

class TestPersonalAcc:
    @pytest.mark.asyncio
    async def test_login(self, make_get_request):
        # make response
        path = '/login'
        valid_credentials = base64.b64encode(b"testuser:testpassword").decode("utf-8")
        headers = {"Authorization": "Basic " + valid_credentials}

        response = await make_get_request(path, headers)

        assert response.status == HTTPStatus.OK