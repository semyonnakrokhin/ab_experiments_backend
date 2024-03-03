import pytest
from httpx import AsyncClient

from apps.src.utils import generate_device_token


class TestGetExperimentsEndpoint:
    _url = "/api/v1/experiments"

    @pytest.mark.parametrize(
        argnames="device_token",
        argvalues=[
            generate_device_token(),
            generate_device_token(),
        ],
    )
    async def test_different_device_token_inputs_success(
        self, async_client: AsyncClient, device_token: str
    ):
        response = await async_client.get(
            url=self._url,
            headers={"Device-Token": device_token} if device_token else {},
        )

        assert response.status_code == 200

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
