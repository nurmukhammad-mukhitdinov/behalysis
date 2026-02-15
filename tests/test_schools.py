"""Tests for /schools endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_school(client: AsyncClient):
    resp = await client.post("/schools", json={"id": 10000001, "name": "Test School"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 10000001
    assert data["name"] == "Test School"


@pytest.mark.asyncio
async def test_create_school_conflict(client: AsyncClient):
    await client.post("/schools", json={"id": 10000001, "name": "School A"})
    resp = await client.post("/schools", json={"id": 10000001, "name": "School B"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_school(client: AsyncClient):
    await client.post("/schools", json={"id": 10000002, "name": "Alpha"})
    resp = await client.get("/schools/10000002")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alpha"


@pytest.mark.asyncio
async def test_get_school_not_found(client: AsyncClient):
    resp = await client.get("/schools/99999999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_school(client: AsyncClient):
    await client.post("/schools", json={"id": 10000003})
    resp = await client.put("/schools/10000003", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_school(client: AsyncClient):
    await client.post("/schools", json={"id": 10000004})
    resp = await client.delete("/schools/10000004")
    assert resp.status_code == 200
    resp = await client.get("/schools/10000004")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_invalid_school_id(client: AsyncClient):
    """8-digit IDs are strictly enforced: too small or too big → 422."""
    resp = await client.post("/schools", json={"id": 1234567, "name": "Bad"})
    assert resp.status_code == 422
    resp = await client.post("/schools", json={"id": 100000000, "name": "Bad"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_schools(client: AsyncClient):
    await client.post("/schools", json={"id": 10000005, "name": "S1"})
    await client.post("/schools", json={"id": 10000006, "name": "S2"})
    resp = await client.get("/schools")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2
