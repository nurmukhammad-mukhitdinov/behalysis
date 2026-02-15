"""Tests for /lesson-reports and related endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import TINY_PNG_B64


def _make_report_payload(**overrides):
    """Build a valid lesson report payload with sensible defaults."""
    base = {
        "class_id": 12345678,
        "school_id": 87654321,
        "class_index": "8-E",
        "lesson_time": "09:30:00",
        "lesson_date": "2026-02-15",
        "students_count": 2,
        "students": [
            {
                "student_id": 11112222,
                "name": "Alice",
                "image": TINY_PNG_B64,
                "attention": 80,
            }
        ],
        "unrecognized_students": [
            {"image": TINY_PNG_B64, "attention": 60}
        ],
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_create_lesson_report(client: AsyncClient):
    payload = _make_report_payload()
    resp = await client.post("/lesson-reports", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["school_id"] == 87654321
    assert data["class_id"] == 12345678
    assert data["class_index"] == "8-E"
    assert data["students_count"] == 2

    # avg_attention = (80 + 60) / 2 = 70.0
    assert data["avg_attention"] == 70.0
    assert data["avg_inattention"] == 30.0

    assert len(data["students"]) == 1
    assert data["students"][0]["attention"] == 80
    assert data["students"][0]["inattention"] == 20
    assert "image_url" in data["students"][0]

    assert len(data["unrecognized_students"]) == 1
    assert data["unrecognized_students"][0]["attention"] == 60
    assert data["unrecognized_students"][0]["inattention"] == 40


@pytest.mark.asyncio
async def test_get_lesson_report(client: AsyncClient):
    create_resp = await client.post("/lesson-reports", json=_make_report_payload())
    report_id = create_resp.json()["id"]

    resp = await client.get(f"/lesson-reports/{report_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == report_id


@pytest.mark.asyncio
async def test_list_lesson_reports(client: AsyncClient):
    await client.post("/lesson-reports", json=_make_report_payload())
    resp = await client.get("/lesson-reports")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_latest_report_for_class(client: AsyncClient):
    # Create two reports for the same class
    payload1 = _make_report_payload(lesson_date="2026-02-14")
    payload2 = _make_report_payload(lesson_date="2026-02-15")
    await client.post("/lesson-reports", json=payload1)
    await client.post("/lesson-reports", json=payload2)

    resp = await client.get("/classes/12345678/lesson-reports/latest")
    assert resp.status_code == 200
    assert resp.json()["lesson_date"] == "2026-02-15"


@pytest.mark.asyncio
async def test_delete_lesson_report(client: AsyncClient):
    create_resp = await client.post("/lesson-reports", json=_make_report_payload())
    report_id = create_resp.json()["id"]

    resp = await client.delete(f"/lesson-reports/{report_id}")
    assert resp.status_code == 200

    resp = await client.get(f"/lesson-reports/{report_id}")
    assert resp.status_code == 404


# ── Validation Tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_count_mismatch(client: AsyncClient):
    """students_count doesn't match actual entries → 422."""
    payload = _make_report_payload(students_count=99)
    resp = await client.post("/lesson-reports", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_bad_attention_range(client: AsyncClient):
    """attention outside 1-100 → 422."""
    payload = _make_report_payload(
        students=[
            {"student_id": 11112222, "image": TINY_PNG_B64, "attention": 0}
        ],
        unrecognized_students=[],
        students_count=1,
    )
    resp = await client.post("/lesson-reports", json=payload)
    assert resp.status_code == 422

    payload2 = _make_report_payload(
        students=[
            {"student_id": 11112222, "image": TINY_PNG_B64, "attention": 101}
        ],
        unrecognized_students=[],
        students_count=1,
    )
    resp2 = await client.post("/lesson-reports", json=payload2)
    assert resp2.status_code == 422


@pytest.mark.asyncio
async def test_bad_student_id(client: AsyncClient):
    """student_id not 8 digits → 422."""
    payload = _make_report_payload(
        students=[
            {"student_id": 999, "image": TINY_PNG_B64, "attention": 50}
        ],
        unrecognized_students=[],
        students_count=1,
    )
    resp = await client.post("/lesson-reports", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_bad_ids_in_payload(client: AsyncClient):
    """class_id or school_id not 8 digits → 422."""
    payload = _make_report_payload(class_id=123)
    resp = await client.post("/lesson-reports", json=payload)
    assert resp.status_code == 422

    payload2 = _make_report_payload(school_id=123)
    resp2 = await client.post("/lesson-reports", json=payload2)
    assert resp2.status_code == 422
