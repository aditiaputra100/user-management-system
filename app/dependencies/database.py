from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session, DeclarativeBase, sessionmaker
from app.dependencies.setting import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


if "sqlite" in settings.database_dialect:
    DATABASE_URL: str = f"{settings.database_dialect}:///{settings.database_name}"
else:
    DATABASE_URL = URL.create(
        drivername=settings.database_dialect, 
        username=settings.database_username, 
        password=settings.database_password, 
        host=settings.database_host, 
        port=settings.database_port, 
        database=settings.database_name).render_as_string(hide_password=False)

print(DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine, autoflush=False) as session:
        yield session
