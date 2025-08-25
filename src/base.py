from abc import ABC, abstractmethod

class Parser(ABC):
    """
    Абстрактный класс для создания классов для работы с API
    """

    @abstractmethod
    def load_vacancies(self, keyword):
        pass

class FileWorker(ABC):

    @abstractmethod
    def add_vacancy(self, vacancy):
        """ Добавление вакансий в файл"""
        pass

    @abstractmethod
    def get_vacancy_info(self):
        """Получение данных из файла по указанным критериям"""
        pass

    @abstractmethod
    def delete_vacancy(self):
        """Удаление информации о вакансиях"""
        pass