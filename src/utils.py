from typing import Any, Mapping, Optional

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









def filter_vacancies(vacancies_list, filter_words):
    """
    Функция фильтрует вакансии по ключевым словам
    :param vacancies_list:
    :param filter_words:
    :return:
    """
    pass

def get_vacancies_by_salary(vacancies, salary_rang):
    """
    Функция фильтрует вакансии по зарплате
    :param vacancies: список вакансий
    :param salary_rang: желаемая зарплата
    :return:
    """
    pass

def sort_get_top_vacancies(vacancies, top_n):
    """
    Функция сортирует вакансии по зарплате и выдаёт топовые
    :param vacancies: список вакансий
    :param top_n: пользователь указывает, какое количество топ-вакансий ему показать
    :return:
    """