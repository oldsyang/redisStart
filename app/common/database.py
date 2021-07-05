import traceback

import databases
from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import config

db_engine = create_engine(
    config.DB_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

_db = None


async def get_db() -> Database:
    global _db
    if _db is None:
        import traceback
        try:
            db = databases.Database(config.DB_URL.replace('+pymysql', ''))
            await db.connect()
        except:
            traceback.print_exc()
        else:
            _db = db
    return _db


class AioDB():
    async def __aenter__(self):
        import traceback
        try:
            db = databases.Database(config.DB_URL.replace('+pymysql', ''))
            await db.connect()
        except:
            traceback.print_exc()
        self.db = db
        return db

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            traceback.print_exc()
        await self.db.disconnect()
