from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.config import logger
from app.database import init_db, get_db
from app.models import Job
from app.schemas import JobCreate, JobUpdate, JobResponse
from app.llm import extract_job_info

app = FastAPI(title="Job Search Helper")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    logger.info("Application started on http://127.0.0.1:8000")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def serve_frontend():
    """Раздача главной страницы"""
    return FileResponse("app/static/index.html")


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


# LLM Endpoints


@app.post("/api/extract-job-info")
async def extract_job_info_endpoint(request: dict):
    """Извлечение title и company из описания вакансии"""
    job_description = request.get("job_description", "")
    
    if not job_description:
        raise HTTPException(status_code=400, detail="job_description is required")
    
    result = extract_job_info(job_description)
    return result


# CRUD Endpoints для Jobs


@app.post("/api/jobs", response_model=JobResponse, status_code=201)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Создание новой вакансии"""
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    logger.info(f"POST /api/jobs | 201 Created | Job ID: {db_job.id}")
    return db_job


@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(db: Session = Depends(get_db)):
    """Получить список всех вакансий"""
    jobs = db.query(Job).all()
    logger.info(f"GET /api/jobs | 200 OK | {len(jobs)} jobs returned")
    return jobs


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Получить одну вакансию по ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.put("/api/jobs/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Обновить вакансию"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Автозаполнение дат при смене статуса
    if job_update.status:
        if job_update.status == "applied" and not job.applied_date:
            job.applied_date = datetime.now()
            logger.info(f"Job {job_id}: applied_date set automatically")
        
        if job_update.status in ["offer", "rejected"] and not job.response_date:
            job.response_date = datetime.now()
            if job.applied_date:
                job.days_to_response = (job.response_date - job.applied_date).days
            logger.info(f"Job {job_id}: response_date and days_to_response set automatically")
    
    # Обновляем поля
    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    logger.info(f"PUT /api/jobs/{job_id} | 200 OK")
    return job


@app.delete("/api/jobs/{job_id}", status_code=204)
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Удалить вакансию"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    logger.info(f"DELETE /api/jobs/{job_id} | 204 No Content")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

