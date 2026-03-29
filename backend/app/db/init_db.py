from sqlalchemy.exc import SQLAlchemyError

import app.models  # noqa: F401
from app.db.base_class import Base
from app.db.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def check_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True
    except SQLAlchemyError:
        return False
