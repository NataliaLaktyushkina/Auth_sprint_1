from http import HTTPStatus

import pytest

from testdata.test_data_genres import genre_ids_for_test, genres_all
from testdata.test_data_person import person_ids_for_test, persons_all, persons_keys, person_film, persons_search

PAGE_SIZE = 10


def check_keys(response_dict, keys):
    for key in keys:
        if key not in response_dict:
            return False
    return True


class TestPersonalAcc:

    @pytest.mark.parametrize('genre_id, expected', genre_ids_for_test)
    @pytest.mark.asyncio
    async def test_genre_id(self, es_client, redis_client, load_genres_to_elastic,
                            make_get_request, genre_id, expected):
        # make response
        path = '/'.join(('/genres', genre_id))
        response = await make_get_request(path)

        assert response.status == HTTPStatus.OK
        assert response.body == expected

