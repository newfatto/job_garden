import json
from typing import Optional, Tuple, Union
from src.files import JSONSaver


class Vacancy:
    """
    Класс для работы с вакансиями. Класс поддерживает методы сравнения вакансий между собой по зарплате и
    валидирует данные, которыми инициализируются его атрибуты.
    Способами валидации данных может быть проверка, указана или нет зарплата. В этом случае выставлять значение
    зарплаты 0 или «Зарплата не указана» в зависимости от структуры класса.
    """


    def __init__(self, name: str, city: str, salary_currency: str, salary_from: int,
                 salary_to: int, responsibility: str, url: str):
        """
        Инициализация объекта Vacancy
        :param name: Название вакансии
        :param city: Город вакансии
        :param salary_currency: Валюта зарплаты
        :param salary_from: Минимальная зарплата
        :param salary_to: Максимальная зарплата
        :param responsibility: Обязанности
        :param url: Ссылка на вакансию
        """
        try:
            self.name = name if name else 'Название не указано'
            self.city = city if city else 'Город не указан'
            self.salary_currency = salary_currency if salary_currency else 'Валюта не указана'
            self.salary_from = salary_from if salary_from else 'Минимальная зарплата не указана'
            self.salary_to = salary_to if salary_to else 'Максимальная зарплата не указана'
            self.responsibility = responsibility if responsibility else 'Обязанности не указаны'
            self.url = url if url else 'URL не указан'
        except Exception as e:
            print(f'При инициализации возникла ошибка: {e}')


    @staticmethod
    def from_hh_json_to_vacancy(vacancy_info: dict) -> Tuple[
        Optional[str],  # name
        Optional[str],  # city
        Optional[str],  # salary_currency
        Optional[Union[int, None]],  # salary_from
        Optional[Union[int, None]],  # salary_to
        Optional[str],  # responsibility
        Optional[str]   # url
    ] | None:
        """
        Функция принимает на вход словарь с информацией о вакансии и подготавливает аргументы для инициирования Vacancy
        :param vacancy_info: dict
        :return: атрибуты, необходимые для инициализации объекта класса Vacancy
        """
        try:

            # Проверяем, что vacancy_info не пустой
            if not vacancy_info:
                return None

            name = vacancy_info.get('name', 'Вакансия без названия')

            area = vacancy_info.get('area')
            city = area.get('name', 'Город не указан') if area else 'Город не указан'

            # Проверяем наличие salary перед доступом к его полям
            salary_info = vacancy_info.get('salary', {})
            salary_currency = salary_info.get('currency', 'Валюта не указана')
            salary_from = salary_info.get('from', 0)
            salary_to = salary_info.get('to', 0)

            snippet = vacancy_info.get('snippet', {})
            responsibility = snippet.get('responsibility', 'Должностные обязанности не указаны')
            url = vacancy_info.get('url', 'url вакансии не указан')

            return name, city, salary_currency, salary_from, salary_to, responsibility, url

        except Exception as e:
            print(f'При загрузке информации о вакансии возникла ошибка: {e}')
            return None


    @classmethod
    def cast_to_object_list(cls, vacancies_list: json) -> list["Vacancy"]:
        """
        Преобразование набора данных из JSON в список объектов Vacancy
        :param vacancies_list: JSON файл со списком вакансий
        :return:
        """
        vacancy_objects = []
        for vacancy_data in vacancies_list:
            try:
                # Получаем данные из JSON
                vacancy_params = cls.from_hh_json_to_vacancy(vacancy_data)
                if vacancy_params:
                    # Создаем объект Vacancy
                    vacancy = Vacancy(*vacancy_params)
                    vacancy_objects.append(vacancy)
            except Exception as e:
                print(f'Ошибка при создании объекта вакансии: {e}')
        return vacancy_objects


if __name__ == '__main__':

    file = JSONSaver()
    vacancies_json = file.load_from_json()  # Получаем список словарей из JSON

    # Создаем список объектов Vacancy
    vacancy_objects = []
    for vacancy_data in vacancies_json:
        try:
            # Получаем параметры для создания объекта
            params = Vacancy.from_hh_json_to_vacancy(vacancy_data)
            if params:
                # Создаем объект Vacancy с полученными параметрами
                vacancy = Vacancy(*params)
                vacancy_objects.append(vacancy)
        except Exception as e:
            print(f'Ошибка при создании объекта вакансии: {e}')

    # Теперь можно работать со списком объектов
    num = 1
    for vac in vacancy_objects:

        print(
            f"{num}Вакансия: {vac.name}, Город: {vac.city}, Зарплата: {vac.salary_from}-{vac.salary_to} {vac.salary_currency}"
        )
        num += 1