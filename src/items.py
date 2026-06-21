import datetime as dt
import dataclasses as dc

from typing import Any

from src.settings import settings
from src.core.database import Database

db = Database()


@dc.dataclass(slots=True)
class Article:
    icon: str = None
    title: str = None
    summary: str = None
    publisher: str = None
    authors: list[str] = None
    category: str = None
    sentiment: str = None
    sentiment_score: float = None
    article_type: str = None
    published: dt.datetime = None
    modified: dt.datetime = None
    tags: list[str] = None
    body: str = None
    url: str = None
    images: list[str] = None

    def insert_to_db(self, table_name: str = "articles") -> bool:
        """ inserts the profile items into the Database object """
        if not self.body:
            return False

        keys, values = [], []
        for k, v in self:
            keys.append(k)
            values.append(str(v))
        values = tuple(values)
        keys = tuple(keys)
        placeholders: str = "(" + ",".join("?" for _ in keys) + ")"

        status = db.insert(
            sql_query=f"INSERT INTO {table_name} {keys} VALUES {placeholders}",
            values=values,
        )

        if status:
            settings["ARTICLES_FOUND"].value += 1
        return status

    def get(self, key: str) -> Any:
        """ get attribute value """
        return getattr(self, key)

    def as_dict(self) -> dict:
        return dc.asdict(self)

    def __iter__(self):
        for f in dc.fields(self):
            yield f.name, getattr(self, f.name)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any):
        setattr(self, key, value)

    def __str__(self) -> str:
        return str(dc.asdict(self))

    def __add__(self, other):
        return Article(
            **{**dc.asdict(self), **dc.asdict(other)}
        )
