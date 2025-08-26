from typing import Any, Dict

from src.vacancy import Vacancy


def test_from_hh_dict_and_str() -> None:
    """Vacancy.from_hh_dict корректно парсит поля, __str__ не падает."""
    raw: Dict[str, Any] = {
        "id": "X1",
        "name": "Data Engineer",
        "area": {"name": "Москва"},
        "salary": {"from": 100000, "to": 200000, "currency": "RUR"},
        "snippet": {"requirement": "ETL", "responsibility": "Пайплайны"},
        "url": "https://api.hh.ru/vacancy/X1",
        "alternate_url": "https://hh.ru/vacancy/X1",
        "employer": {"name": "Data Corp"},
    }
    v = Vacancy.from_hh_dict(raw)
    assert v.name == "Data Engineer"
    assert v.city == "Москва"
    assert v.currency == "RUR"
    assert "зарплата" in str(v).lower()


def test_comparison_effective_salary() -> None:
    """Сравнения работают по «эффективной» зарплате (from/to)."""
    low = Vacancy(
        id="L",
        name="Low",
        city="-",
        salary_from=100000,
        salary_to=None,
        currency="RUR",
        requirement=None,
        responsibility=None,
        url="-",
    )
    mid = Vacancy(
        id="M",
        name="Mid",
        city="-",
        salary_from=100000,
        salary_to=200000,
        currency="RUR",
        requirement=None,
        responsibility=None,
        url="-",
    )
    high = Vacancy(
        id="H",
        name="High",
        city="-",
        salary_from=None,
        salary_to=300000,
        currency="RUR",
        requirement=None,
        responsibility=None,
        url="-",
    )

    assert low < mid < high
    assert high > mid > low

    another_low = Vacancy(
        id="L2",
        name="Low2",
        city="-",
        salary_from=100000,
        salary_to=None,
        currency="RUR",
        requirement=None,
        responsibility=None,
        url="-",
    )
    assert low == another_low


def test_to_dict_roundtrip() -> None:
    """to_dict возвращает согласованный с hh.ru словарь (ключевые поля на месте)."""
    v = Vacancy(
        id="T1",
        name="Test",
        city="Москва",
        salary_from=150_000,
        salary_to=200_000,
        currency="RUR",
        requirement="Python",
        responsibility="Разработка",
        url="https://api.hh.ru/vacancy/T1",
        alternate_url="https://hh.ru/vacancy/T1",
        employer="Test Co",
    )
    d = v.to_dict()
    assert d["id"] == "T1"
    assert d["area"]["name"] == "Москва"
    assert d["salary"]["from"] == 150_000
    assert d["salary"]["to"] == 200_000
    assert d["salary"]["currency"] == "RUR"
    assert d["snippet"]["requirement"] == "Python"
    assert d["url"].startswith("https://")
