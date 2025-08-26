from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

JSON_FILE_PATH = BASE_DIR / "data" / "vacancies.json"

JSON_FILE_PATH_STR = str(JSON_FILE_PATH)
