from httpx import AsyncClient


class TestGetExperimentStatsEndpoint:
    _url = "/pages/experiment-stats"

    async def test_successful_response(self, async_client: AsyncClient):
        response = await async_client.get(url=self._url)
        assert response.status_code == 200

    async def test_page_not_found(self, async_client: AsyncClient):
        response = await async_client.get(url="/nonexistent-page")
        assert response.status_code == 404
