import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker


DEFAULT_DATABASE_URL = "mysql+pymysql://root:mysql@localhost/streetlens?charset=utf8mb4"

DATABASE_URL = os.getenv("STREETLENS_DATABASE_URL", DEFAULT_DATABASE_URL)

Base = declarative_base()


def _ensure_database_exists():
    url = make_url(DATABASE_URL)
    database_name = url.database
    if not database_name:
        return

    server_url = url.set(database=None)
    server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT", future=True)
    safe_database_name = database_name.replace("`", "``")

    with server_engine.connect() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{safe_database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )

    server_engine.dispose()


engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db():
    _ensure_database_exists()
    from database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
