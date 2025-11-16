from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL, logger

# Создаём engine для SQLite
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Нужно для SQLite
)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Dependency для получения сессии БД в FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создание всех таблиц в БД"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

