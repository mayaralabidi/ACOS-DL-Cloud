import pytest


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_sessions_empty(client):
    r = await client.get("/sessions/")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_get_session_not_found(client):
    r = await client.get("/sessions/does-not-exist")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cancel_session_not_found(client):
    r = await client.delete("/sessions/does-not-exist")
    assert r.status_code == 404