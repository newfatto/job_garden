from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytest

from src.files import JSONSaver
from src.vacancy import Vacancy


@pytest.fixture
def json_saver(tmp_path: Path) -> JSONSaver:
    """
    JSONSaver на временном файле (каждый тест — свой файл).
    """
    return JSONSaver(filename=str(tmp_path / "vacancies_test.json"))


@pytest.fixture(scope="session")
def raw_items() -> List[Dict[str, Any]]:
    """
    Мини-набор «сырых» вакансий (как с hh.ru) + дубликат первой записи.
    Достаточно для тестов дедупликации/фильтров.
    """
    a1: Dict[str, Any] = {
        "id": "A1",
        "name": "Python Developer",
        "area": {"name": "Москва"},
        "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
        "snippet": {"requirement": "Python, Django", "responsibility": "Разработка API"},
        "url": "https://api.hh.ru/vacancy/A1",
        "alternate_url": "https://hh.ru/vacancy/A1",
        "employer": {"name": "Best Company"},
    }
    b2: Dict[str, Any] = {
        "id": "B2",
        "name": "Backend Engineer",
        "area": {"name": "Санкт-Петербург"},
        "salary": {"from": 120000, "to": None, "currency": "RUR"},
        "snippet": {"requirement": "Flask, SQL", "responsibility": "Поддержка сервисов"},
        "url": "https://api.hh.ru/vacancy/B2",
        "alternate_url": "https://hh.ru/vacancy/B2",
        "employer": {"name": "Nice Co"},
    }
    return [a1, b2, dict(a1)]  # дубликат A1 — для проверки «без дублей»


@pytest.fixture(scope="session")
def vacancies(raw_items: List[Dict[str, Any]]) -> List[Vacancy]:
    """
    Те же данные, но преобразованные в доменные объекты Vacancy.
    """
    return Vacancy.cast_to_object_list(raw_items)


@pytest.fixture
def make_vac() -> Callable[..., Vacancy]:
    """
    Фабрика для краткого создания Vacancy в тестах.

    Пример:
        v = make_vac(name="Python Dev", salary_from=150_000)
    """

    def _make_vac(
        *,
        name: str,
        city: str = "Москва",
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        currency: Optional[str] = "RUR",
        requirement: Optional[str] = None,
        responsibility: Optional[str] = None,
        id_: Optional[str] = None,
    ) -> Vacancy:
        return Vacancy(
            id=id_,
            name=name,
            city=city,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            requirement=requirement,
            responsibility=responsibility,
            url="https://example.com",
            alternate_url=None,
            employer=None,
        )

    return _make_vac
