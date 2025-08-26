import json
import os
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Union

from config import JSON_FILE_PATH_STR
from src.base import FileWorker
from src.utils import pick_identity

if TYPE_CHECKING:
    from src.vacancy import Vacancy


class JSONSaver(FileWorker):
    """
    Коннектор для работы с JSON-файлом вакансий.

    - добавляет вакансии в файл без перезаписи всего файла;
    - не допускает дублей (по id / url / alternate_url);
    - умеет фильтровать и удалять записи.
    """

    def __init__(self, filename: str = JSON_FILE_PATH_STR) -> None:
        """
        :param filename: путь к JSON-файлу для хранения вакансий
        """
        self._filename = filename

    def _read_all(self) -> List[Dict[str, Any]]:
        """Безопасное чтение всего файла как списка словарей."""
        try:
            # пустой или отсутствующий файл — просто []
            if not os.path.exists(self._filename) or os.path.getsize(self._filename) == 0:
                return []
            with open(self._filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            # битый JSON — начинаем с чистого листа
            return []
        except OSError as e:
            print(f"Ошибка чтения файла: {e}")
            return []

    def _write_all(self, data: List[Dict[str, Any]]) -> None:
        """Полная запись списка словарей в файл."""
        try:
            # гарантируем наличие папки
            os.makedirs(os.path.dirname(self._filename) or ".", exist_ok=True)
            with open(self._filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except OSError as e:
            print(f"Ошибка записи в файл: {e}")

    def load_from_json(self) -> List[Dict[str, Any]]:
        """
        Прочитать все вакансии из файла.
        :return: список вакансий (каждая вакансия — словарь)
        """
        return self._read_all()

    def save_to_json(self, vacancies: Iterable[Mapping[str, Any]]) -> None:
        current = self._read_all()
        index: Dict[str, int] = {}

        for i, v_existing in enumerate(current):
            ident = pick_identity(v_existing)
            if ident:
                index[ident] = i

        for v_new in vacancies:
            if not isinstance(v_new, Mapping):
                print("Предупреждение: пропущен элемент не-словарь при сохранении.")
                continue

            ident = pick_identity(v_new)
            if ident and ident in index:
                current[index[ident]] = dict(v_new)  # обновляем запись
            else:
                current.append(dict(v_new))
                if ident:
                    index[ident] = len(current) - 1

        self._write_all(current)

    def add_vacancy(self, vacancy: Union[Mapping[str, Any], "Vacancy"]) -> None:
        """
        Добавить одну вакансию в файл.
        :param vacancy: словарь вакансии или объект Vacancy с методом to_dict()
        """
        if isinstance(vacancy, Mapping):
            self.save_to_json([vacancy])
            return

        if hasattr(vacancy, "to_dict") and callable(getattr(vacancy, "to_dict")):
            try:
                self.save_to_json([vacancy.to_dict()])  # type: ignore[attr-defined]
            except Exception as e:
                print(f"Ошибка сериализации Vacancy: {e}")
            return

        raise TypeError("add_vacancy ожидает Mapping или объект Vacancy с to_dict().")

    def get_vacancy_info(
        self,
        *,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        min_salary: Optional[int] = None,
        currency: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Вернёт список вакансий, удовлетворяющих критериям.
        :param keyword: ключевое слово (ищется в названии и описании)
        :param city: город (area.name или address.city)
        :param min_salary: минимальная желаемая "from" (salary.from >= min_salary)
        :param currency: валюта зарплаты (salary.currency)
        :return: отфильтрованный список словарей вакансий
        """
        data = self._read_all()
        kw = (keyword or "").strip().lower()
        city_norm = (city or "").strip().lower()
        cur_norm = (currency or "").strip().upper()

        def match(v: Dict[str, Any]) -> bool:
            if kw:
                name = str(v.get("name", "")).lower()
                resp = str(v.get("snippet", {}).get("responsibility", "")).lower()
                req = str(v.get("snippet", {}).get("requirement", "")).lower()
                if kw not in name and kw not in resp and kw not in req:
                    return False

            if city_norm:
                area_name = str(v.get("area", {}).get("name", "")).lower()
                addr_city = str(v.get("address", {}).get("city", "")).lower()
                if city_norm not in area_name and city_norm not in addr_city:
                    return False

            if cur_norm:
                sal = v.get("salary") or {}
                if not isinstance(sal, dict) or (sal.get("currency") or "").upper() != cur_norm:
                    return False

            if isinstance(min_salary, int):
                sal = v.get("salary") or {}
                sal_from = sal.get("from")
                if sal_from is None:
                    return False
                try:
                    if int(sal_from) < int(min_salary):
                        return False
                except Exception:
                    return False

            return True

        return [v for v in data if match(v)]

    def delete_vacancy(
        self,
        *,
        vacancy_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> int:
        """
        Удалить вакансию(и) по `id` или `url`/`alternate_url`.
        :param vacancy_id: строковый ID вакансии hh.ru
        :param url: ссылка ('url' или 'alternate_url')
        :return: количество удалённых записей
        """
        if not vacancy_id and not url:
            raise ValueError("Нужно указать vacancy_id или url для удаления.")

        before = self._read_all()

        def should_delete(v: Dict[str, Any]) -> bool:
            if vacancy_id and str(v.get("id", "")) == vacancy_id:
                return True
            if url and (v.get("url") == url or v.get("alternate_url") == url):
                return True
            return False

        after = [v for v in before if not should_delete(v)]
        deleted = len(before) - len(after)
        if deleted:
            self._write_all(after)
        return deleted
