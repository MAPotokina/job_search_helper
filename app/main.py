from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import logger
from app.database import init_db, get_db

app = FastAPI(title="Job Search Helper")


@app.on_event("startup")
async def startup_event():
    logger.info("Application started on http://127.0.0.1:8000")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    return {"message": "Job Search Helper API"}


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint для проверки БД"""
    try:
        # Проверка подключения к БД
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "database": "disconnected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

