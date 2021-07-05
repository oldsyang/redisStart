import inspect
from typing import List, Union

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.engine.result import RowProxy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

from settings import config
from utils.tools import ObjectDict, now_time

IGNORE_ATTRS = ['redis', 'stats']
MC_KEY_ITEM_BY_ID = '%s:%s'


class PropertyHolder(type):
    """
    We want to make our class with som useful properties
    and filter the private properties.
    """

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        new_cls.property_fields = []

        for attr in list(attrs) + sum([list(vars(base))
                                       for base in bases], []):
            if attr.startswith('_') or attr in IGNORE_ATTRS:
                continue
            if isinstance(getattr(new_cls, attr), property):
                new_cls.property_fields.append(attr)
        return new_cls


@as_declarative()
class Base():
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return "_".join([config.DB_TABLE_PREFIX, cls.__name__.lower()])

    @property
    def url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/'

    @property
    def canonical_url(self):
        pass


class ModelMeta(Base.__class__, PropertyHolder):
    ...


class BaseModel(Base, metaclass=ModelMeta):
    """
        Sqlalchemy is unable to support asynchronous, we
        have to use `databases` to excute sql in async, which
        is inrevelent to `Base` model. However we can implement
        both sync and async version.
    """

    __abstract__ = True
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=now_time, index=True)

    @classmethod
    def to_dict(cls,
                results: Union[RowProxy, List[RowProxy]]) -> Union[List[dict], dict]:
        if not isinstance(results, list):
            return ObjectDict({col: val for col, val in zip(results.keys(), results)})
        list_dct = []
        for row in results:
            list_dct.append(ObjectDict({col: val for col, val in zip(row.keys(), row)}))
        return list_dct

    async def to_async_dict(self, **data):
        """some coroutine properties like `post.html_content`
        we have to use it like `await post.html_content`
        however if we use it in Mako template, we have
        to process it into the obj can use point access.
        """
        rv = {key: value for key, value in data.items()}
        for field in self.property_fields:
            coro = getattr(self, field)
            if inspect.iscoroutine(coro):
                rv[field] = await coro
            else:
                rv[field] = coro
        rv['url'] = self.url
        return ObjectDict(rv)

    @classmethod
    async def async_get(cls, *args, **kwargs):
        pass

    @classmethod
    async def sync_first(cls, *args, **kwargs):
        pass

    @classmethod
    async def sync_filter(cls, *args, **kwargs):
        pass

    @classmethod
    async def sync_all(cls, *args, **kwargs):
        pass

    def sync_create(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def sync_delete(self):
        pass

    def sync_save(self, *args, **kwargs):
        pass

    def get_db_key(self, key):
        return f'{self.__class__.__name__}/{self.id}/props/{key}'


if __name__ == '__main__':
    pass
