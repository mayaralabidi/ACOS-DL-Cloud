import pytest


@pytest.mark.asyncio
async def test_list_products_initially_empty(client):
    response = await client.get("/products/")
    assert response.status_code == 200
    assert response.json() == []