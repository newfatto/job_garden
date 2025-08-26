from typing import Any, Dict, List, Mapping, Optional
from unittest.mock import patch

import pytest

from src.api import HeadHunterAPI


class _FakeResponse:
    """Класс-замена requests.Response для моков."""

    def __init__(self, status_code: int, data: Dict[str, Any]) -> None:
        self.status_code: int = status_code
        self._data: Dict[str, Any] = data
        self.text: str = str(data)

    def json(self) -> Dict[str, Any]:
        return self._data


def test_load_vacancies_pagination() -> None:
    pages: List[Dict[str, Any]] = [
        {"page": 0, "pages": 3, "per_page": 2, "items": [{"id": "1"}, {"id": "2"}]},
        {"page": 1, "pages": 3, "per_page": 2, "items": [{"id": "3"}]},
        {"page": 2, "pages": 3, "per_page": 2, "items": [{"id": "4"}]},
    ]
    api = HeadHunterAPI(user_agent="test", per_page=2)

    def fake_get(
        url: str,
        *,
        headers: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> _FakeResponse:
        page = int((params or {}).get("page", 0))
        data = pages[page] if 0 <= page < len(pages) else {"page": page, "pages": len(pages), "items": []}
        return _FakeResponse(200, data)

    with patch.object(api._session, "get", side_effect=fake_get):  # type: ignore[attr-defined]
        items = api.load_vacancies("python", max_items=10)

    assert [it["id"] for it in items] == ["1", "2", "3", "4"]


def test_load_vacancies_respects_max_items() -> None:
    pages: List[Dict[str, Any]] = [
        {"page": 0, "pages": 2, "per_page": 5, "items": [{"id": "1"}, {"id": "2"}]},
        {"page": 1, "pages": 2, "per_page": 5, "items": [{"id": "3"}, {"id": "4"}]},
    ]
    api = HeadHunterAPI(user_agent="test", per_page=5)

    def fake_get(
        url: str,
        *,
        headers: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> _FakeResponse:
        page = int((params or {}).get("page", 0))
        return _FakeResponse(200, pages[page] if page < len(pages) else {"items": []})

    with patch.object(api._session, "get", side_effect=fake_get):  # type: ignore[attr-defined]
        items = api.load_vacancies("python", max_items=2)

    assert len(items) == 2
    assert [i["id"] for i in items] == ["1", "2"]


def test_load_vacancies_breaks_on_empty_batch() -> None:
    api = HeadHunterAPI(user_agent="test", per_page=50)

    def fake_get(
        url: str,
        *,
        headers: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> _FakeResponse:
        return _FakeResponse(200, {"page": 0, "pages": 1, "items": []})

    with patch.object(api._session, "get", side_effect=fake_get):  # type: ignore[attr-defined]
        assert api.load_vacancies("python", max_items=100) == []


def test_request_error_is_raised() -> None:
    api = HeadHunterAPI(user_agent="test", per_page=10)

    def fake_get(
        url: str,
        *,
        headers: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> _FakeResponse:
        return _FakeResponse(500, {"error": "boom"})

    with patch.object(api._session, "get", side_effect=fake_get):  # type: ignore[attr-defined]
        with pytest.raises(RuntimeError):
            api.load_vacancies("python")


def test_per_page_adjusts_to_remaining() -> None:
    api = HeadHunterAPI(user_agent="test", per_page=50)
    captured: List[Dict[str, Any]] = []

    def fake_get(
        url: str,
        *,
        headers: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> _FakeResponse:
        captured.append(dict(params or {}))
        return _FakeResponse(200, {"page": 0, "pages": 1, "items": []})

    with patch.object(api._session, "get", side_effect=fake_get):  # type: ignore[attr-defined]
        _ = api.load_vacancies("python", max_items=1)

    assert captured, "ожидался хотя бы один вызов .get"
    first = captured[0]
    assert first["per_page"] == 1
    assert first["page"] == 0
    assert first["text"] == "python"
