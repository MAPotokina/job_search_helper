from fastapi import FastAPI
from app.config import logger

app = FastAPI(title="Job Search Helper")


@app.on_event("startup")
async def startup_event():
    logger.info("Application started on http://127.0.0.1:8000")


@app.get("/")
async def root():
    return {"message": "Job Search Helper API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

