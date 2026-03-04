from src.core.database import Database
from src.util.utils import path


if __name__ == '__main__':
    database = Database()

    for table in ['articles']:
        database.execute(f'DROP TABLE IF EXISTS {table};')

        file_path: str = path('..', '.db')
        file_path = path(file_path, "sql")
        file_path = path(file_path, f'{table}.sql')

        with open(file=file_path, mode='r', encoding='utf-8', errors='ignore') as file:
            database.execute(
                file.read()
            )
