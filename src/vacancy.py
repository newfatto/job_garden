from typing import Any, Iterable, List, Mapping, Optional


class Vacancy:
    """
    Доменная модель вакансии.

    Атрибуты:
        id: строковый идентификатор вакансии (hh.ru) или None.
        name: название вакансии.
        city: город (area.name).
        salary_from: нижняя граница зарплаты (int) или None.
        salary_to: верхняя граница зарплаты (int) или None.
        currency: валюта зарплаты (например, 'RUR') или None.
        requirement: требования (snippet.requirement) или None.
        responsibility: обязанности (snippet.responsibility) или None.
        url: API-ссылка на вакансию (обязательное поле, при пустом — "-").
        alternate_url: читаемая ссылка на вакансию или None.
        employer: название работодателя или None.

    Сравнения выполняются по «эффективной» зарплате:
    берем среднее из (salary_from, salary_to); если указан один край — берем его;
    если зарплата не указана, считаем 0.
    """

    __slots__ = (
        "id",
        "name",
        "city",
        "salary_from",
        "salary_to",
        "currency",
        "requirement",
        "responsibility",
        "url",
        "alternate_url",
        "employer",
    )

    def __init__(
        self,
        *,
        id: Optional[str],
        name: str,
        city: str,
        salary_from: Optional[int],
        salary_to: Optional[int],
        currency: Optional[str],
        requirement: Optional[str],
        responsibility: Optional[str],
        url: str,
        alternate_url: Optional[str] = None,
        employer: Optional[str] = None,
    ) -> None:
        """
        Инициализация валидированными значениями.

        :param id: строковый идентификатор вакансии hh.ru или None
        :param name: название вакансии
        :param city: город
        :param salary_from: нижняя граница зарплаты или None
        :param salary_to: верхняя граница зарплаты или None
        :param currency: валюта зарплаты или None
        :param requirement: требования (может быть None)
        :param responsibility: обязанности (может быть None)
        :param url: ссылка на вакансию (обязательное поле)
        :param alternate_url: читаемая ссылка на вакансию
        :param employer: название работодателя
        """
        self.id = self._validate_id(id)
        self.name = self._validate_str(name, default="Вакансия без названия")
        self.city = self._validate_str(city, default="Город не указан")
        self.salary_from = self._validate_salary(salary_from)
        self.salary_to = self._validate_salary(salary_to)
        self.currency = self._normalize_currency(currency)
        self.requirement = self._coerce_optional_str(requirement)
        self.responsibility = self._coerce_optional_str(responsibility)
        self.url = self._validate_url(url)
        self.alternate_url = self._coerce_optional_str(alternate_url)
        self.employer = self._coerce_optional_str(employer)

    @staticmethod
    def _validate_id(value: Optional[str]) -> Optional[str]:
        """Приводит идентификатор к строке без пустых значений."""
        if value is None:
            return None
        s = str(value).strip()
        return s or None

    @staticmethod
    def _validate_str(value: Any, *, default: str) -> str:
        """Обязательная строка с дефолтом для пустых/None."""
        s = str(value).strip() if value is not None else ""
        return s or default

    @staticmethod
    def _coerce_optional_str(value: Any) -> Optional[str]:
        """Необязательная строка: пустые строки → None."""
        if value is None:
            return None
        s = str(value).strip()
        return s or None

    @staticmethod
    def _validate_salary(value: Any) -> Optional[int]:
        """Корректная зарплата: целое неотрицательное или None."""
        if value is None:
            return None
        try:
            iv = int(value)
        except (TypeError, ValueError):
            return None
        return iv if iv >= 0 else None

    @staticmethod
    def _normalize_currency(value: Any) -> Optional[str]:
        """Валюта в верхнем регистре (например, RUR) или None."""
        if not value:
            return None
        s = str(value).strip().upper()
        return s or None

    @staticmethod
    def _validate_url(value: Any) -> str:
        """URL обязателен; пустой → подставляем заглушку '-'."""
        s = str(value).strip() if value is not None else ""
        return s or "-"


    def _effective_salary(self) -> int:
        """
        Эффективное значение для сравнения вакансий:
        среднее из (salary_from, salary_to); один край — он и есть значение;
        отсутствуют оба — 0.
        :return: целое число для сравнения
        """
        a = self.salary_from
        b = self.salary_to
        if a is not None and b is not None:
            return (a + b) // 2
        if a is not None:
            return a
        if b is not None:
            return b
        return 0

    # Сравнения по зарплате
    def __eq__(self, other: object) -> bool:
        """
        Равенство по эффективной зарплате.
        :param other: другой объект c возможностью применить к нему _effective_salary
        :return: True/False или NotImplemented для чужих типов
        """
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._effective_salary() == other._effective_salary()

    def __lt__(self, other: "Vacancy") -> bool:
        """
        Меньше по эффективной зарплате (используется при сортировке).
        """
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._effective_salary() < other._effective_salary()

    def __le__(self, other: "Vacancy") -> bool:
        """Меньше или равно по эффективной зарплате."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: "Vacancy") -> bool:
        """Больше по эффективной зарплате."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return other.__lt__(self)

    def __ge__(self, other: "Vacancy") -> bool:
        """Больше или равно по эффективной зарплате."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return other.__le__(self)

    def __str__(self) -> str:
        """
        Читаемое представление вакансии.
        :return: строка с названием, городом и вилкой зарплаты
        """
        sal_from = self.salary_from if self.salary_from is not None else "-"
        sal_to = self.salary_to if self.salary_to is not None else "-"
        cur = self.currency or ""
        return f"{self.name} — {self.city}; зарплата: от {sal_from} до {sal_to} {cur}".strip()

    def to_dict(self) -> dict:
        """
        Представление вакансии в словаре (для JSONSaver).
        :return: словарь с данными вакансии
        """
        return {
            "id": self.id,
            "name": self.name,
            "area": {"name": self.city},
            "salary": {
                "from": self.salary_from,
                "to": self.salary_to,
                "currency": self.currency,
            },
            "snippet": {
                "requirement": self.requirement,
                "responsibility": self.responsibility,
            },
            "url": self.url,
            "alternate_url": self.alternate_url,
            "employer": {"name": self.employer} if self.employer else None,
        }


    @classmethod
    def from_hh_dict(cls, data: Mapping[str, Any]) -> "Vacancy":
        """
        Построить Vacancy из словаря ответа hh.ru.

        Ожидаемые поля:
            id, name, area.name, salary.{from,to,currency},
            snippet.{requirement,responsibility}, url, alternate_url, employer.name
        :param data: словарь одной вакансии из API hh.ru
        :return: объект Vacancy
        """
        area = data.get("area") or {}
        salary = data.get("salary") or {}
        snippet = data.get("snippet") or {}
        employer = data.get("employer") or {}

        return cls(
            id=str(data.get("id")) if data.get("id") is not None else None,
            name=str(data.get("name") or "").strip(),
            city=str(area.get("name") or "").strip(),
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            currency=salary.get("currency"),
            requirement=snippet.get("requirement"),
            responsibility=snippet.get("responsibility"),
            url=str(data.get("url") or "").strip(),
            alternate_url=str(data.get("alternate_url") or "").strip() or None,
            employer=str(employer.get("name") or "").strip() or None,
        )

    @staticmethod
    def cast_to_object_list(items: Iterable[Mapping[str, Any]]) -> List["Vacancy"]:
        """
        Преобразовать коллекцию словарей HH в список объектов Vacancy.
        Некорректные элементы пропускаются.

        :param items: итерируемая коллекция словарей hh.ru
        :return: список вакансий
        """
        result: List[Vacancy] = []
        for d in items:
            try:
                result.append(Vacancy.from_hh_dict(d))
            except Exception:
                continue
        return result
