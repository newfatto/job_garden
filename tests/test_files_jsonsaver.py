from typing import Any, Dict, List

from src.files import JSONSaver


def test_save_without_duplicates_and_update(json_saver: JSONSaver, raw_items: List[Dict[str, Any]]) -> None:
    """save_to_json не пишет дубли (по id/url), а add_vacancy обновляет существующую запись."""
    json_saver.save_to_json(raw_items)
    data = json_saver.load_from_json()
    assert len(data) == 2

    updated: Dict[str, Any] = dict(data[0] if data[0]["id"] == "A1" else data[1])
    updated["salary"] = {"from": 180000, "to": 250000, "currency": "RUR"}
    json_saver.add_vacancy(updated)

    fresh = json_saver.load_from_json()
    a1 = next(v for v in fresh if v["id"] == "A1")
    assert a1["salary"]["from"] == 180000


def test_get_vacancy_info_filters(json_saver: JSONSaver, raw_items: List[Dict[str, Any]]) -> None:
    """Фильтры по keyword/city/min_salary/currency возвращают корректные элементы."""
    json_saver.save_to_json(raw_items)
    found = json_saver.get_vacancy_info(
        keyword="python",
        city="москва",
        min_salary=140_000,
        currency="RUR",
    )
    assert len(found) == 1
    assert found[0]["id"] == "A1"


def test_delete_by_id_and_url(json_saver: JSONSaver, raw_items: List[Dict[str, Any]]) -> None:
    """Удаление по id и по url работает и возвращает число удалённых записей."""
    json_saver.save_to_json(raw_items)
    deleted_by_id = json_saver.delete_vacancy(vacancy_id="A1")
    assert deleted_by_id == 1
    left = [v["id"] for v in json_saver.load_from_json()]
    assert left == ["B2"]
    deleted_by_url = json_saver.delete_vacancy(url="https://hh.ru/vacancy/B2")
    assert deleted_by_url == 1
    assert json_saver.load_from_json() == []
