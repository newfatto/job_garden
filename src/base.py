from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional

class Parser(ABC):
    """
    Абстрактный клиент для API сервисов с вакансиями.
    Обязывает реализовать защищённый метод сетевого запроса и публичный сбор вакансий.
    """

    @abstractmethod
    def _request(self, params: Mapping[str, Any]) -> Dict[str, Any]:
        """
        Приватный/защищённый метод подключения к API.

        :param params: параметры запроса (text, page, per_page и т. п.)
        :return: JSON-ответ API в виде словаря
        :raises Exception: любая ошибка сетевого уровня или неуспешный статус
        """
        pass

    @abstractmethod
    def load_vacancies(self, keyword: str, *, max_items: int = 100) -> List[Dict[str, Any]]:
        """
        Получить список «сырых» вакансий (словарей) по ключевому слову.

        :param keyword: поисковая фраза
        :param max_items: верхний предел количества результатов
        :return: список словарей из ответа API (обычно data["items"])
        """
        pass

class FileWorker(ABC):
    """
    Абстракция над хранилищем вакансий (файл/БД/облако).
    Обязывает уметь: добавлять запись, выбирать по критериям, удалять запись(и).
    """

    @abstractmethod
    def add_vacancy(self, vacancy: Any) -> None:
        """
        Добавить одну вакансию в хранилище.

        Ожидается словарь или объект, который можно сериализовать (например, имеет метод to_dict()).
        """
        pass

    @abstractmethod
    def get_vacancy_info(
        self,
        *,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        min_salary: Optional[int] = None,
        currency: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить вакансии по критериям.

        :param keyword: ключевое слово в названии/описании
        :param city: город (area.name/address.city)
        :param min_salary: нижняя граница зарплаты (salary.from >= min_salary)
        :param currency: валюта (salary.currency)
        :return: список словарей вакансий
        """
        pass

    @abstractmethod
    def delete_vacancy(
        self,
        *,
        vacancy_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> int:
        """
        Удалить запись(и) по id или по ссылке.

        :param vacancy_id: строковый идентификатор вакансии
        :param url: url или alternate_url
        :return: количество удалённых записей
        """
        pass
