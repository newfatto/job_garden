from src.base import FileWorker
import json
from config import JSON_FILE_PATH_STR


class JSONSaver(FileWorker):
    """
    Класс для сохранения информации о вакансиях в JSON-файл
    """
    def __init__(self, filename: str = JSON_FILE_PATH_STR):
        self.filename = filename

    def load_from_json(self) -> list:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except IOError as e:
            print(f"Ошибка чтения файла: {e}")
            return []

    def save_to_json(self, vacancies: list) -> json:
        """
        Сохраняет вакансии в файл json
        :param vacancies: список вакансий, который должен быть преобразован в json файл
        :return: json файл
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(vacancies, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Ошибка записи в файл: {e}")


    def add_vacancy(self, vacancy: 'Vacancy'):
        """
        Добавление вакансий в файл
        :param vacancy: экземпляр класса Vacancy
        :return:
        """
        try:
            from src.vacancy import Vacancy
            current_data = self.load_from_json()
            current_data.append(vacancy)
            self.save_to_json(current_data)
        except TypeError:
            print(f'В файл можно добавить только вакансию')
        except Exception as e:
            print(f'Возникла ошибка: {e}')


    def get_vacancy_info(self):
        """Получение данных из файла по указанным критериям"""
        pass


    def delete_vacancy(self):
        """Удаление информации о вакансиях"""
        pass