import sqlite3
import threading

from src.settings import settings
from src.util.decorators import catch_exceptions
from typing import Generator, Any, Optional


class Database(threading.Thread):
    def __init__(self, database_file_path: str = settings["DATABASE"]) -> None:
        super(Database, self).__init__()
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.db_path = database_file_path
        self.mutex = threading.Lock()

    def _connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=180.0)
            self.cursor = self.conn.cursor()

    def _close(self):
        if isinstance(self.conn, sqlite3.Connection):
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            self.conn = None
            self.cursor = None

    @catch_exceptions
    def fetch_all(self, table_name: str) -> Generator[tuple[Any], None, None]:
        """
         fetch all data from table
         :yield: Place datatype in a tuple
        """
        with self.mutex:
            self._connect()
            for row in self.cursor.execute(f'SELECT * FROM {table_name};'):
                yield row
            self._close()

    @catch_exceptions
    def insert(self, values: Optional[tuple], sql_query: str) -> bool:
        """
         execute a sql query to insert into database

         :param values: all the values in a tuple for the database insertion query.
         :param sql_query: the full insert SQL query to execute

         :rtype: bool
         :return: True if inserted successfully False otherwise
        """
        with self.mutex:
            self._connect()
            try: self.cursor.execute(sql_query, values)
            except sqlite3.IntegrityError: return False
            else: self.conn.commit()
            self._close()

        return True

    @catch_exceptions
    def delete_record(self, record_id: int,  table_name: str = 'articles') -> None:
        """ delete a record from a table """
        with self.mutex:
            self._connect()
            self.cursor.execute(f'DELETE FROM {table_name} WHERE id={record_id};')
            self.conn.commit()
            self._close()

    @catch_exceptions
    def execute(self, sql_query: str) -> sqlite3.Cursor:
        """ execute a sql query """
        with self.mutex:
            self._connect()
            cur = self.cursor.execute(sql_query)
            self.conn.commit()
            self._close()
        return cur

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._close()

    def __del__(self) -> None:
        self._close()
