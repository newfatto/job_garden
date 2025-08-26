from typing import Any, Iterable, Mapping, Optional, Tuple, List, TYPE_CHECKING
from src.vacancy import Vacancy
import re

if TYPE_CHECKING:
    from src.vacancy import Vacancy

def pick_identity(v: Mapping[str, Any]) -> Optional[str]:
    """
    Вернёт уникальный идентификатор вакансии для исключения дубликации.
    Сначала пытаемся взять 'id', затем 'url' или 'alternate_url'.

    :param v: словарь с описанием вакансии
    :return: строковый идентификатор или None, если не найден
    """
    for key in ("id", "url", "alternate_url"):
        val = v.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return None


def filter_vacancies(vacancies_list: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Фильтрует вакансии по совпадению хотя бы одного ключевого слова
    в полях name / requirement / responsibility (регистронезависимо).

    :param vacancies_list: список объектов Vacancy
    :param filter_words: список ключевых слов, например ["django", "flask"]
    :return: отфильтрованный список
    """
    if not filter_words:
        return vacancies_list
    keys = [w.lower() for w in filter_words]

    def ok(v: Vacancy) -> bool:
        hay = " ".join([
            v.name or "",
            v.requirement or "",
            v.responsibility or "",
        ]).lower()
        return any(k in hay for k in keys)

    return [v for v in vacancies_list if ok(v)]

def get_vacancies_by_salary(
    vacancies: List[Vacancy],
    salary_range: Tuple[Optional[int], Optional[int]],
) -> List[Vacancy]:
    """
    Оставляет вакансии, чья «эффективная» зарплата попадает в диапазон.
    Диапазон может быть (None, X) или (X, None).

    :param vacancies: список Vacancy
    :param salary_range: (low, high) — границы или None
    :return: отфильтрованный список
    """
    low, high = salary_range
    def within(v: Vacancy) -> bool:
        val = v._effective_salary()
        if low is not None and val < low:
            return False
        if high is not None and val > high:
            return False
        return True

    return [v for v in vacancies if within(v)]

def sort_get_top_vacancies(vacancies: List[Vacancy], top_n: int) -> List[Vacancy]:
    """
    Сортирует по убыванию зарплаты и возвращает top-N.

    :param vacancies: список Vacancy
    :param top_n: количество топ-вакансий
    :return: отсортированный срез
    """
    n = max(0, int(top_n))
    if n == 0:
        return []
    return sorted(vacancies, reverse=True)[:n]

def parse_salary_range(s: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Разобрать строку диапазона зарплаты.

    Поддерживаем форматы:
      "", "150000", "100000-200000", "100000 - 200000",
      " - 200000", "100000 - ", "100000—200000" (длинное тире)

    Любые пробелы и типы тире нормализуются. Нецифровые символы вокруг игнорируются.

    :param s: строка с диапазоном
    :return: (low, high) — нижняя/верхняя граница или None, если не указана
    """
    s = (s or "").strip()
    if not s:
        return None, None

    # нормализуем разные тире к обычному минусу
    s = s.replace("—", "-").replace("–", "-")

    # убираем лишние пробелы вокруг минуса
    s = re.sub(r"\s*-\s*", "-", s.strip())

    if "-" in s:
        left, right = s.split("-", 1)
        low = int(left) if left.isdigit() else None
        high = int(right) if right.isdigit() else None
        return low, high

    # одиночное число — считаем нижней границей
    return (int(s) if s.isdigit() else None, None)


def print_vacancies(vs: List["Vacancy"]) -> None:
    """
    Вывести вакансии в консоль.

    :param vs: список объектов Vacancy
    """
    if not vs:
        print("Ничего не найдено.")
        return

    for i, v in enumerate(vs, 1):
        print(f"{i:>2}. {v}")