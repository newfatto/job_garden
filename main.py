from __future__ import annotations
from typing import List, Optional, Tuple

from src.api import HeadHunterAPI
from src.vacancy import Vacancy
from src.files import JSONSaver
from src.utils import (parse_salary_range, print_vacancies, filter_vacancies, get_vacancies_by_salary,
                       sort_get_top_vacancies)


def user_interaction() -> None:
    """
    Консольный интерфейс:
    - запрос к hh.ru по ключевому слову
    - фильтр по словам
    - фильтр по зарплате (диапазон)
    - сортировка по зарплате и top-N
    - сохранение в JSON без дублей
    """
    api = HeadHunterAPI(user_agent="job-garden/1.0", per_page=50)
    saver = JSONSaver()

    keyword = input("Введите поисковый запрос (например, Python): ").strip()
    if not keyword:
        print("Пустой запрос — выхожу.")
        return

    top_n = int(input("Сколько топ-вакансий показать: ").strip() or "10")
    words = input("Ключевые слова для фильтра (через пробел, можно пусто): ").split()
    salary_s = input("Желаемая зарплата или диапазон (например, 120000-200000, можно пусто): ")
    low, high = parse_salary_range(salary_s)
    print("Идёт поиск подходящих вакансий...")

    raw = api.load_vacancies(keyword, max_items=500)

    vacancies = Vacancy.cast_to_object_list(raw)

    if words:
        vacancies = filter_vacancies(vacancies, words)
    vacancies = get_vacancies_by_salary(vacancies, (low, high))

    top = sort_get_top_vacancies(vacancies, top_n)

    print_vacancies(top)

    saver.save_to_json([v.to_dict() for v in top])
    print(f"\nСохранено в файл: {len(top)} записей.")


if __name__ == "__main__":
    user_interaction()
