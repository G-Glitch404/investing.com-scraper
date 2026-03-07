import psutil
from src.core.database import Database
from src.util.utils import path


def rebuild_database() -> None:
    database: Database = Database()

    for table in ['articles', ]:
        database.execute(f'DROP TABLE IF EXISTS {table};')

        file_path: str = path('..', '.db')
        file_path: str = path(file_path, 'sql')
        file_path: str = path(file_path, f'{table}.sql')

        with open(file=file_path, mode='r', encoding='utf-8', errors='ignore') as file:
            database.execute(
                file.read()
            )


def clean_processes():
    for process in psutil.process_iter():
        try:
            process_name: str = process.name().lower()
            if not ("chromedriver" in process_name or "chrome" in process_name): continue
            process.kill()
            process.wait(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return
