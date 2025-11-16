import time
import json
from openai import OpenAI

from app.config import (
    OPENAI_API_KEY, 
    OPENAI_MODEL, 
    OPENAI_TEMPERATURE, 
    OPENAI_MAX_TOKENS,
    MAX_JOB_DESCRIPTION_LENGTH,
    MAX_RESUME_LENGTH,
    logger
)
from app.prompts import PROMPTS
from app.database import SessionLocal
from app.models import LLMLog


# Инициализация OpenAI клиента
client = OpenAI(api_key=OPENAI_API_KEY)


def log_llm_call(function_name: str, status: str, execution_time: float, 
                 tokens_used: int = None, error_message: str = None):
    """Логирование LLM вызова в БД"""
    db = SessionLocal()
    try:
        log = LLMLog(
            function_name=function_name,
            status=status,
            execution_time=execution_time,
            tokens_used=tokens_used,
            error_message=error_message
        )
        db.add(log)
        db.commit()
    finally:
        db.close()


def extract_job_info(job_description: str) -> dict:
    """Извлечение названия позиции и компании из описания вакансии"""
    start_time = time.time()
    
    # Обрезаем длинный текст
    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        job_description = job_description[:MAX_JOB_DESCRIPTION_LENGTH]
        logger.info(f"Job description truncated to {MAX_JOB_DESCRIPTION_LENGTH} chars")
    
    try:
        prompt = PROMPTS["extract_job_info"].format(job_description=job_description)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        result_text = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        execution_time = time.time() - start_time
        
        # Парсим JSON ответ
        result = json.loads(result_text)
        
        # Логируем успех
        log_llm_call("extract_job_info", "success", execution_time, tokens_used)
        logger.info(f"LLM | extract_job_info | SUCCESS | {execution_time:.2f}s | {tokens_used} tokens")
        
        return result
        
    except json.JSONDecodeError as e:
        execution_time = time.time() - start_time
        error_msg = f"JSON parsing error: {str(e)}"
        
        log_llm_call("extract_job_info", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | extract_job_info | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"title": "Unknown Position", "company": "Unknown Company"}


def analyze_visa_sponsorship(job_description: str) -> dict:
    """Анализ наличия visa sponsorship в описании вакансии"""
    start_time = time.time()
    
    # Обрезаем длинный текст
    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        job_description = job_description[:MAX_JOB_DESCRIPTION_LENGTH]
        logger.info(f"Job description truncated to {MAX_JOB_DESCRIPTION_LENGTH} chars")
    
    try:
        prompt = PROMPTS["visa_sponsorship"].format(job_description=job_description)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        result_text = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        execution_time = time.time() - start_time
        
        # Парсим JSON ответ
        result = json.loads(result_text)
        
        # Логируем успех
        log_llm_call("analyze_visa_sponsorship", "success", execution_time, tokens_used)
        logger.info(f"LLM | analyze_visa_sponsorship | SUCCESS | {execution_time:.2f}s | {tokens_used} tokens")
        
        return result
        
    except json.JSONDecodeError as e:
        execution_time = time.time() - start_time
        error_msg = f"JSON parsing error: {str(e)}"
        
        log_llm_call("analyze_visa_sponsorship", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | analyze_visa_sponsorship | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"has_sponsorship": None, "analysis": "Unable to determine"}
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        log_llm_call("analyze_visa_sponsorship", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | analyze_visa_sponsorship | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"has_sponsorship": None, "analysis": "Unable to determine"}


def analyze_resume_match(resume: str, job_description: str) -> dict:
    """Анализ соответствия резюме требованиям вакансии"""
    start_time = time.time()
    
    # Обрезаем длинные тексты
    if len(resume) > MAX_RESUME_LENGTH:
        resume = resume[:MAX_RESUME_LENGTH]
        logger.info(f"Resume truncated to {MAX_RESUME_LENGTH} chars")
    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        job_description = job_description[:MAX_JOB_DESCRIPTION_LENGTH]
        logger.info(f"Job description truncated to {MAX_JOB_DESCRIPTION_LENGTH} chars")
    
    try:
        prompt = PROMPTS["resume_match"].format(
            resume=resume,
            job_description=job_description
        )
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        result_text = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        execution_time = time.time() - start_time
        
        # Парсим JSON ответ
        result = json.loads(result_text)
        
        # Логируем успех
        log_llm_call("analyze_resume_match", "success", execution_time, tokens_used)
        logger.info(f"LLM | analyze_resume_match | SUCCESS | {execution_time:.2f}s | {tokens_used} tokens")
        
        return result
        
    except json.JSONDecodeError as e:
        execution_time = time.time() - start_time
        error_msg = f"JSON parsing error: {str(e)}"
        
        log_llm_call("analyze_resume_match", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | analyze_resume_match | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"match_percentage": 0, "analysis": "Unable to analyze"}
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        log_llm_call("analyze_resume_match", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | analyze_resume_match | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"match_percentage": 0, "analysis": "Unable to analyze"}


def generate_cover_letter(resume: str, template: str, job_description: str, 
                         job_title: str, company: str) -> dict:
    """Генерация персонализированного cover letter"""
    start_time = time.time()
    
    # Обрезаем длинные тексты
    if len(resume) > MAX_RESUME_LENGTH:
        resume = resume[:MAX_RESUME_LENGTH]
        logger.info(f"Resume truncated to {MAX_RESUME_LENGTH} chars")
    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        job_description = job_description[:MAX_JOB_DESCRIPTION_LENGTH]
        logger.info(f"Job description truncated to {MAX_JOB_DESCRIPTION_LENGTH} chars")
    
    try:
        prompt = PROMPTS["cover_letter"].format(
            resume=resume,
            template=template,
            job_title=job_title,
            company=company,
            job_description=job_description
        )
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        result_text = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        execution_time = time.time() - start_time
        
        # Для cover letter возвращаем просто текст (не JSON)
        # Логируем успех
        log_llm_call("generate_cover_letter", "success", execution_time, tokens_used)
        logger.info(f"LLM | generate_cover_letter | SUCCESS | {execution_time:.2f}s | {tokens_used} tokens")
        
        return {"cover_letter": result_text}
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        log_llm_call("generate_cover_letter", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | generate_cover_letter | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"cover_letter": "Unable to generate cover letter"}

