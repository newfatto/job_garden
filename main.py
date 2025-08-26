from src.api import HeadHunterAPI
from src.files import JSONSaver
from src.utils import (
    _prompt_nonempty,
    _prompt_positive_int,
    _prompt_salary_range,
    filter_vacancies,
    get_vacancies_by_salary,
    print_vacancies,
    sort_get_top_vacancies,
)
from src.vacancy import Vacancy


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

    keyword: str = _prompt_nonempty("Введите поисковый запрос (например, Python): ")
    top_n: int = _prompt_positive_int(
        "Сколько топ-вакансий показать (до 500; если пропустить, выведется 10 вакансий): ", default=10
    )

    words_input = input("Ключевые слова для фильтра (через пробел, можно не указывать): ").strip()
    words = words_input.split() if words_input else []

    low, high = _prompt_salary_range(
        "Желаемая зарплата или диапазон (число или диапазон, например, 120000-200000; " "можно не указывать): "
    )

    print("Идёт поиск подходящих вакансий...")

    try:
        raw = api.load_vacancies(keyword, max_items=500)
    except Exception as e:
        print(f"Ошибка запроса к hh.ru: {e}")
        return

    vacancies = Vacancy.cast_to_object_list(raw)

    if words:
        vacancies = filter_vacancies(vacancies, words)
    vacancies = get_vacancies_by_salary(vacancies, (low, high))
    top = sort_get_top_vacancies(vacancies, top_n)

    print_vacancies(top)

    try:
        saver.save_to_json([v.to_dict() for v in top])
        print(f"\nСохранено в файл: {len(top)} записей.")
    except Exception as e:
        print(f"Не удалось сохранить в JSON: {e}")


if __name__ == "__main__":
    user_interaction()
