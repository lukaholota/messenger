import pytest


@pytest.mark.asyncio
async def test_read_root(async_client):
    response = await async_client.get('/api/v1/')

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World from API v1!"}
