from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.config import logger
from app.database import init_db, get_db
from app.models import Job
from app.schemas import JobCreate, JobUpdate, JobResponse
from app.llm import analyze_job_complete, generate_cover_letter

app = FastAPI(title="Job Search Helper")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    logger.info("Application started on http://127.0.0.1:8000")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def serve_frontend():
    """Serve main page"""
    return FileResponse("app/static/index.html")


@app.get("/stats")
async def serve_stats():
    """Serve statistics page"""
    return FileResponse("app/static/stats.html")


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify database connection"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "database": "disconnected"}


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """LLM usage statistics"""
    from sqlalchemy import func
    from app.models import LLMLog
    from app.config import COST_PER_1K_TOKENS
    
    # Overall statistics
    total_calls = db.query(func.count(LLMLog.id)).scalar()
    successful_calls = db.query(func.count(LLMLog.id)).filter(
        LLMLog.status == "success"
    ).scalar()
    total_tokens = db.query(func.sum(LLMLog.tokens_used)).scalar() or 0
    total_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS
    
    # Breakdown by function
    stats_by_function = db.query(
        LLMLog.function_name,
        func.count(LLMLog.id).label("count"),
        func.sum(LLMLog.tokens_used).label("tokens"),
        func.avg(LLMLog.execution_time).label("avg_time")
    ).group_by(LLMLog.function_name).all()
    
    function_stats = []
    for stat in stats_by_function:
        tokens = stat.tokens or 0
        cost = (tokens / 1000) * COST_PER_1K_TOKENS
        function_stats.append({
            "function_name": stat.function_name,
            "call_count": stat.count,
            "tokens_used": tokens,
            "avg_execution_time": round(stat.avg_time, 2) if stat.avg_time else 0,
            "estimated_cost": round(cost, 4)
        })
    
    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "total_tokens": total_tokens,
        "estimated_cost": round(total_cost, 2),
        "by_function": function_stats
    }


# LLM Endpoints


@app.post("/api/generate-cover-letter/{job_id}", response_model=JobResponse)
async def generate_cover_letter_endpoint(job_id: int, db: Session = Depends(get_db)):
    """Generate personalized cover letter"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.job_description:
        raise HTTPException(status_code=400, detail="Job description is required")
    
    # Read resume and base template
    try:
        with open("templates/user_resume.txt", "r") as f:
            resume = f.read()
        with open("templates/cover_letter_base.txt", "r") as f:
            template = f.read()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Template file not found: {str(e)}")
    
    result = generate_cover_letter(
        resume=resume,
        template=template,
        job_description=job.job_description,
        job_title=job.title,
        company=job.company
    )
    
    # Save result
    job.cover_letter = result.get("cover_letter")
    db.commit()
    db.refresh(job)
    
    logger.info(f"POST /api/generate-cover-letter/{job_id} | Cover letter generated")
    return job


# CRUD Endpoints for Jobs


@app.post("/api/jobs", response_model=JobResponse, status_code=201)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create new job with automatic AI analysis"""
    
    # If description exists, do comprehensive analysis
    if job.job_description:
        try:
            with open("templates/user_resume.txt", "r") as f:
                resume = f.read()
            
            # Comprehensive analysis: title, company, visa, match
            analysis = analyze_job_complete(job.job_description, resume)
            
            # If title/company not specified, take from analysis
            title = job.title if job.title else analysis.get("title", "Unknown Position")
            company = job.company if job.company else analysis.get("company", "Unknown Company")
            
            # Ensure correct type for has_visa_sponsorship (only bool or None)
            visa_value = analysis.get("visa_sponsorship")
            if visa_value is True or visa_value == True:
                has_visa = True
            elif visa_value is False or visa_value == False:
                has_visa = False
            else:
                has_visa = None
            
            # Convert dict to JSON string if needed
            visa_analysis = analysis.get("visa_analysis")
            if isinstance(visa_analysis, dict):
                visa_analysis = json.dumps(visa_analysis, ensure_ascii=False)
                logger.warning(f"visa_analysis was dict, converted to JSON string")
            
            match_analysis = analysis.get("match_analysis")
            if isinstance(match_analysis, dict):
                match_analysis = json.dumps(match_analysis, ensure_ascii=False)
                logger.warning(f"match_analysis was dict, converted to JSON string")
            
            # Log what will be saved
            logger.info(f"Saving to DB - visa_analysis length: {len(visa_analysis) if visa_analysis else 0} chars")
            logger.info(f"Saving to DB - visa_analysis preview: {visa_analysis[:200] if visa_analysis else 'None'}...")
            logger.info(f"Saving to DB - match_analysis length: {len(match_analysis) if match_analysis else 0} chars")
            
            # Create job with analysis results
            db_job = Job(
                title=title,
                company=company,
                job_url=job.job_url,
                job_description=job.job_description,
                status=job.status,
                has_visa_sponsorship=has_visa,
                sponsorship_analysis=visa_analysis,
                resume_match_percentage=analysis.get("match_percentage"),
                match_analysis=match_analysis
            )
            logger.info(f"Job analyzed: visa={analysis.get('visa_sponsorship')}, match={analysis.get('match_percentage')}%")
            
        except FileNotFoundError:
            logger.warning("Resume file not found, creating job without analysis")
            db_job = Job(**job.dict())
        except Exception as e:
            logger.error(f"Error during job analysis: {e}")
            db_job = Job(**job.dict())
    else:
        db_job = Job(**job.dict())
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    logger.info(f"POST /api/jobs | 201 Created | Job ID: {db_job.id}")
    return db_job


@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(db: Session = Depends(get_db)):
    """Get list of all jobs"""
    jobs = db.query(Job).all()
    logger.info(f"GET /api/jobs | 200 OK | {len(jobs)} jobs returned")
    return jobs


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get single job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.put("/api/jobs/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Update job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Auto-fill dates when status changes
    if job_update.status:
        if job_update.status == "applied" and not job.applied_date:
            job.applied_date = datetime.now()
            logger.info(f"Job {job_id}: applied_date set automatically")
        
        if job_update.status in ["offer", "rejected"] and not job.response_date:
            job.response_date = datetime.now()
            if job.applied_date:
                job.days_to_response = (job.response_date - job.applied_date).days
                logger.info(f"Job {job_id}: response_date and days_to_response set automatically")
    
    # Update fields
    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    logger.info(f"PUT /api/jobs/{job_id} | 200 OK")
    return job


@app.delete("/api/jobs/{job_id}", status_code=204)
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    logger.info(f"DELETE /api/jobs/{job_id} | 204 No Content")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

