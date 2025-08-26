from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING, Callable

import pytest

if TYPE_CHECKING:
    from src.vacancy import Vacancy

from src.utils import (
    pick_identity,
    filter_vacancies,
    get_vacancies_by_salary,
    sort_get_top_vacancies,
    parse_salary_range,
    print_vacancies,
)

def test_pick_identity_priority_order() -> None:
    v: Dict[str, Any] = {
        "id": "ID123",
        "url": "http://u",
        "alternate_url": "http://alt",
    }
    assert pick_identity(v) == "ID123"


def test_pick_identity_fallbacks_and_none() -> None:
    assert pick_identity({"alternate_url": "http://alt"}) == "http://alt"
    assert pick_identity({"url": "http://u"}) == "http://u"
    assert pick_identity({"name": "no ids"}) is None

@pytest.mark.parametrize(
    "s, expected",
    [
        ("", (None, None)),
        ("150000", (150000, None)),
        ("100000-200000", (100000, 200000)),
        ("100000 - 200000", (100000, 200000)),
        (" - 200000", (None, 200000)),
        ("100000 - ", (100000, None)),
        ("100000—200000", (100000, 200000)),
        ("abc-200000", (None, 200000)),
        ("100000-xyz", (100000, None)),
    ],
)
def test_parse_salary_range_cases(s: str, expected: Tuple[Optional[int], Optional[int]]) -> None:
    assert parse_salary_range(s) == expected


def test_filter_vacancies_case_insensitive_and_fields(make_vac: Callable[..., "Vacancy"]) -> None:
    v1 = make_vac(name="Python Dev", requirement="Django", salary_from=100_000)
    v2 = make_vac(name="Backend", responsibility="Поддержка Flask", salary_from=120_000)
    v3 = make_vac(name="QA Engineer", salary_from=90_000)
    out = filter_vacancies([v1, v2, v3], ["python", "flask"])
    assert out == [v1, v2]

def test_filter_vacancies_empty_words_returns_same_list(make_vac: Callable[..., "Vacancy"]) -> None:
    vs = [make_vac(name="A"), make_vac(name="B")]
    assert filter_vacancies(vs, []) == vs


def test_get_vacancies_by_salary_inclusive_bounds(make_vac: Callable[..., "Vacancy"]) -> None:
    v_low  = make_vac(name="Low",  salary_from=100_000)
    v_mid  = make_vac(name="Mid",  salary_from=100_000, salary_to=200_000)
    v_high = make_vac(name="High", salary_to=250_000)
    res = get_vacancies_by_salary([v_low, v_mid, v_high], (150_000, 250_000))
    assert res == [v_mid, v_high]

def test_get_vacancies_by_salary_open_range(make_vac: Callable[..., "Vacancy"]) -> None:
    v1 = make_vac(name="A", salary_from=80_000)
    v2 = make_vac(name="B", salary_from=120_000)
    assert get_vacancies_by_salary([v1, v2], (None, 100_000)) == [v1]
    assert get_vacancies_by_salary([v1, v2], (100_000, None)) == [v2]


def test_sort_get_top_vacancies_desc_and_limit(make_vac: Callable[..., "Vacancy"]) -> None:
    v1 = make_vac(name="L", salary_from=100_000)                    # 100k
    v2 = make_vac(name="M", salary_from=100_000, salary_to=200_000)  # 150k
    v3 = make_vac(name="H", salary_to=300_000)                       # 300k
    top2 = sort_get_top_vacancies([v1, v2, v3], 2)
    assert [v.name for v in top2] == ["H", "M"]

def test_sort_get_top_vacancies_zero_or_negative(make_vac: Callable[..., "Vacancy"]) -> None:
    vs = [make_vac(name="A", salary_from=1)]
    assert sort_get_top_vacancies(vs, 0) == []
    assert sort_get_top_vacancies(vs, -5) == []


def test_print_vacancies_nonempty_captures_stdout(capsys: pytest.CaptureFixture[str], make_vac: Callable[..., "Vacancy"]) -> None:
    v1 = make_vac(name="Python Dev", salary_from=100_000)
    v2 = make_vac(name="Backend", salary_from=120_000)
    print_vacancies([v1, v2])
    out = capsys.readouterr().out
    assert "1." in out and "Python Dev" in out
    assert "2." in out and "Backend" in out

def test_print_vacancies_empty_list(capsys: pytest.CaptureFixture[str]) -> None:
    print_vacancies([])
    out = capsys.readouterr().out.strip().lower()
    assert "ничего не найдено" in out
