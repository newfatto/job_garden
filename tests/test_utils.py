from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple

import pytest

if TYPE_CHECKING:
    from src.vacancy import Vacancy

from src.utils import (
    _prompt_nonempty,
    _prompt_positive_int,
    _prompt_salary_range,
    filter_vacancies,
    get_vacancies_by_salary,
    parse_salary_range,
    pick_identity,
    print_vacancies,
    sort_get_top_vacancies,
)


def test_prompt_nonempty(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Тестируем работу _prompt_nonempty: пропускаем пустой ввод и принимаем корректную строку."""
    inputs = iter(["", "Python"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = _prompt_nonempty("Введите запрос: ")
    assert result == "Python"

    out = capsys.readouterr().out.lower()
    assert "пустой ввод" in out


def test_prompt_positive_int_with_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Тестируем работу _prompt_positive_int: пустой ввод возвращает значение по умолчанию."""
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert _prompt_positive_int("Сколько показать: ", default=10) == 10


def test_prompt_positive_int_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Тестируем работу _prompt_positive_int: некорректные вводы, затем корректное положительное число."""
    inputs = iter(["abc", "0", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert _prompt_positive_int("Сколько показать: ") == 5


def test_prompt_salary_range_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Тестируем работу _prompt_salary_range: пустой ввод возвращает (None, None)."""
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert _prompt_salary_range("Диапазон: ") == (None, None)


def test_prompt_salary_range_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Тестируем работу _prompt_salary_range: корректный диапазон '100000-200000' возвращает границы чисел."""
    monkeypatch.setattr("builtins.input", lambda _: "100000-200000")
    low, high = _prompt_salary_range("Диапазон: ")
    assert (low, high) == (100000, 200000)


def test_pick_identity_priority_order() -> None:
    """Тестируем pick_identity: приоритетное использование id над url и alternate_url."""
    v: Dict[str, Any] = {
        "id": "ID123",
        "url": "http://u",
        "alternate_url": "http://alt",
    }
    assert pick_identity(v) == "ID123"


def test_pick_identity_fallbacks_and_none() -> None:
    """Тестируем pick_identity: fallback к url или alternate_url и возврат None, если их нет."""
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
    """Тестируем parse_salary_range: разные варианты строк и ожидаемые границы диапазона."""
    assert parse_salary_range(s) == expected


def test_filter_vacancies_case_insensitive_and_fields(make_vac: Callable[..., "Vacancy"]) -> None:
    """Тестируем filter_vacancies: поиск ключевых слов в разных полях вакансии (без учёта регистра)."""
    v1 = make_vac(name="Python Dev", requirement="Django", salary_from=100_000)
    v2 = make_vac(name="Backend", responsibility="Поддержка Flask", salary_from=120_000)
    v3 = make_vac(name="QA Engineer", salary_from=90_000)
    out = filter_vacancies([v1, v2, v3], ["python", "flask"])
    assert out == [v1, v2]


def test_filter_vacancies_empty_words_returns_same_list(make_vac: Callable[..., "Vacancy"]) -> None:
    """Тестируем filter_vacancies: при пустом списке слов возвращается тот же список вакансий."""
    vs = [make_vac(name="A"), make_vac(name="B")]
    assert filter_vacancies(vs, []) == vs


def test_get_vacancies_by_salary_inclusive_bounds(make_vac: Callable[..., "Vacancy"]) -> None:
    """Тестируем get_vacancies_by_salary: отбор вакансий, попадающих в указанный диапазон зарплат."""
    v_low = make_vac(name="Low", salary_from=100_000)
    v_mid = make_vac(name="Mid", salary_from=100_000, salary_to=200_000)
    v_high = make_vac(name="High", salary_to=250_000)
    res = get_vacancies_by_salary([v_low, v_mid, v_high], (150_000, 250_000))
    assert res == [v_mid, v_high]


def test_get_vacancies_by_salary_open_range(make_vac: Callable[..., "Vacancy"]) -> None:
    """Тестируем get_vacancies_by_salary: диапазоны с None как нижней или верхней границей."""
    v1 = make_vac(name="A", salary_from=80_000)
    v2 = make_vac(name="B", salary_from=120_000)
    assert get_vacancies_by_salary([v1, v2], (None, 100_000)) == [v1]
    assert get_vacancies_by_salary([v1, v2], (100_000, None)) == [v2]


def test_sort_get_top_vacancies_desc_and_limit(make_vac: Callable[..., "Vacancy"]) -> None:
    """Тестируем sort_get_top_vacancies: сортировка по зарплате и ограничение числа элементов top-N."""
    v1 = make_vac(name="L", salary_from=100_000)  # 100k
    v2 = make_vac(name="M", salary_from=100_000, salary_to=200_000)  # 150k
    v3 = make_vac(name="H", salary_to=300_000)  # 300k
    top2 = sort_get_top_vacancies([v1, v2, v3], 2)
    assert [v.name for v in top2] == ["H", "M"]


def test_sort_get_top_vacancies_zero_or_negative(make_vac: Callable[..., "Vacancy"]) -> None:
    """Тестируем sort_get_top_vacancies: при нуле или отрицательном top-N возвращается пустой список."""
    vs = [make_vac(name="A", salary_from=1)]
    assert sort_get_top_vacancies(vs, 0) == []
    assert sort_get_top_vacancies(vs, -5) == []


def test_print_vacancies_nonempty_captures_stdout(
    capsys: pytest.CaptureFixture[str], make_vac: Callable[..., "Vacancy"]
) -> None:
    """Тестируем print_vacancies: печать списка вакансий в консоль при непустом вводе."""
    v1 = make_vac(name="Python Dev", salary_from=100_000)
    v2 = make_vac(name="Backend", salary_from=120_000)
    print_vacancies([v1, v2])
    out = capsys.readouterr().out
    assert "1." in out and "Python Dev" in out
    assert "2." in out and "Backend" in out


def test_print_vacancies_empty_list(capsys: pytest.CaptureFixture[str]) -> None:
    """Тестируем print_vacancies: вывод сообщения 'ничего не найдено' при пустом списке вакансий."""
    print_vacancies([])
    out = capsys.readouterr().out.strip().lower()
    assert "ничего не найдено" in out
