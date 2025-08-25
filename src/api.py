from typing import Any, Dict, List
from src.base import Parser
from src.files import JSONSaver
import requests
from requests import Session, Response

class HeadHunterAPI(Parser):

    """
    Клиент для работы с API hh.ru.

    Инкапсулирует:
    - базовый URL и заголовки;
    - размер страницы (per_page);
    - HTTP-сессию requests.

    Предоставляет единый публичный метод `load_vacancies`, который
    собирает до `max_items` вакансий по ключевому слову.
    """
    __slots__ = ("_base_url", "_headers", "_per_page", "_session")

    def __init__(self, user_agent: str = "job-garden/1.0", per_page: int = 50) -> None:
        """
        :param user_agent: строка User-Agent для запросов к API
        :param per_page: желаемое количество элементов на страницу (максимум 100 у hh.ru)
        """
        self._base_url: str = "https://api.hh.ru/vacancies"
        self._headers: Dict[str, str] = {"User-Agent": user_agent}
        self._per_page: int = max(1, min(per_page, 100))
        self._session: Session = requests.Session()

    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет GET-запрос к hh.ru и возвращает JSON.

        :param params: словарь query‑параметров (text, page, per_page и т.п.)
        :raises RuntimeError: если API вернул неуспешный статус
        :return: распарсенный JSON-ответ как словарь
        """
        resp: Response = self._session.get(
            self._base_url, headers=self._headers, params=params, timeout=20
        )
        if resp.status_code != 200:
            preview = resp.text[:200] if resp.text else ""
            raise RuntimeError(f"HH API error {resp.status_code}. {preview}")
        return resp.json()


    def load_vacancies(self, keyword: str, *, max_items: int = 2000) -> List[Dict[str, Any]]:
        """
        Получить список вакансий по ключевому слову.

        :param keyword: поисковая фраза (параметр text)
        :param max_items: желаемое максимальное число вакансий в результате
        :return: список словарей из ключа 'items' ответа API
        """
        items: List[Dict[str, Any]] = []
        page: int = 0

        while len(items) < max_items:
            per_page = min(self._per_page, max_items - len(items))
            payload: Dict[str, Any] = {"text": keyword, "page": page, "per_page": per_page}

            data = self._request(payload)
            batch = data.get("items", [])
            if not batch:
                break

            items.extend(batch)

            pages_total = data.get("pages")
            if pages_total is None or page >= int(pages_total) - 1:
                break
            page += 1

        return items

    def __str__(self) -> str:
        """Краткое представление клиента (для логов/отладки)."""
        return f"HeadHunterAPI(base_url={self._base_url!r}, per_page={self._per_page})"


if __name__ == '__main__':
    hh = HeadHunterAPI(user_agent="job-garden/1.0", per_page=50)
    vacancies = hh.load_vacancies("Java")  # ← теперь это список словарей
    JSONSaver().save_to_json(vacancies)  # файл перезапишется (пока так в твоём JSONSaver)

    try:
        hh.load_vacancies("Java")

        # Проверяем результат
        print("Сохранено вакансий:", len(vacancies))
        print("Пример вакансии:", vacancies[0] if vacancies else "Файл пуст")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

