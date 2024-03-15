import pytest
from httpx import AsyncClient

from apps.src.utils import generate_device_token


@pytest.mark.usefixtures("empty_database")
class TestGetExperimentsEndpoint:
    _url = "/api/v1/experiments"
    device_token = generate_device_token()

    async def test_device_token_success(self, async_client: AsyncClient):
        response = await async_client.get(
            url=self._url, headers={"Device-Token": self.device_token}
        )

        assert response.status_code == 200

        experiments_response_lst = response.json()
        assert type(experiments_response_lst) == list

        for experiment in experiments_response_lst:
            if experiment["name"] == "button_color":
                assert experiment["option"] in ("#FF0000", "#00FF00", "#0000FF")
            elif experiment["name"] == "price":
                assert experiment["option"] in (5, 10, 20, 50)
            else:
                assert False

    @pytest.mark.parametrize(
        argnames="device_token, status_code",
        argvalues=[("invalid_device_token", 401), ("", 400)],
    )
    async def test_different_device_token_inputs_exceptions(
        self, async_client: AsyncClient, device_token: str, status_code: int
    ):
        response = await async_client.get(
            url=self._url, headers={"Device-Token": device_token}
        )

        assert response.status_code == status_code
