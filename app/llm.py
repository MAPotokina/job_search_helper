import time
import json
import re
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


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def log_llm_call(function_name: str, status: str, execution_time: float, 
                 tokens_used: int = None, error_message: str = None):
    """Log LLM call to database"""
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


def analyze_job_complete(job_description: str, resume: str) -> dict:
    """Comprehensive job analysis: extract info + sponsorship + resume match"""
    start_time = time.time()
    
    # Truncate long texts
    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        job_description = job_description[:MAX_JOB_DESCRIPTION_LENGTH]
        logger.info(f"Job description truncated to {MAX_JOB_DESCRIPTION_LENGTH} chars")
    if len(resume) > MAX_RESUME_LENGTH:
        resume = resume[:MAX_RESUME_LENGTH]
        logger.info(f"Resume truncated to {MAX_RESUME_LENGTH} chars")
    
    try:
        prompt = PROMPTS["analyze_job_complete"].format(
            job_description=job_description,
            resume=resume
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
        
        # Log raw response for debugging
        logger.info(f"Raw LLM response (first 500 chars): {result_text[:500]}")
        
        # Try to parse as JSON
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError as json_error:
            # If failed, maybe LLM used real newlines instead of \\n
            logger.warning(f"First JSON parse failed: {json_error}, trying to fix newlines")
            logger.info(f"Problematic area: ...{result_text[max(0, json_error.pos-50):json_error.pos+50]}...")
            
            # Use json.dumps for proper string value escaping
            # But first need to find and fix problematic strings
            # Simple approach: replace only dangerous control chars, keeping newlines as \\n
            result_text_fixed = result_text
            # Replace real newlines with escaped versions
            result_text_fixed = result_text_fixed.replace('\r\n', '\\n')  # Windows newlines
            result_text_fixed = result_text_fixed.replace('\n', '\\n')    # Unix newlines
            result_text_fixed = result_text_fixed.replace('\r', '\\n')    # Mac newlines
            result_text_fixed = result_text_fixed.replace('\t', ' ')      # Tabs to spaces
            
            logger.info(f"Fixed text (first 500 chars): {result_text_fixed[:500]}")
            result = json.loads(result_text_fixed)
        
        # Fix has_visa_sponsorship type - must be bool or None, not string
        visa_val = result.get("visa_sponsorship")
        logger.info(f"Raw visa_sponsorship value: {visa_val}, type: {type(visa_val)}")
        
        # Normalize value to Python bool or None
        if visa_val is None or visa_val == "null" or visa_val == "None" or visa_val == "":
            result["visa_sponsorship"] = None
        elif visa_val is True or visa_val == "true" or visa_val == "True" or visa_val == 1:
            result["visa_sponsorship"] = True
        elif visa_val is False or visa_val == "false" or visa_val == "False" or visa_val == 0:
            result["visa_sponsorship"] = False
        else:
            logger.warning(f"Unexpected visa_sponsorship value: {visa_val}, defaulting to None")
            result["visa_sponsorship"] = None
        
        logger.info(f"Normalized visa_sponsorship: {result['visa_sponsorship']}, type: {type(result['visa_sponsorship'])}")
        
        # Log analysis lengths for debugging
        visa_analysis_len = len(result.get("visa_analysis", "")) if result.get("visa_analysis") else 0
        match_analysis_len = len(result.get("match_analysis", "")) if result.get("match_analysis") else 0
        logger.info(f"Analysis lengths - visa: {visa_analysis_len} chars, match: {match_analysis_len} chars")
        logger.info(f"visa_analysis preview: {result.get('visa_analysis', '')[:200]}...")
        
        log_llm_call("analyze_job_complete", "success", execution_time, tokens_used)
        logger.info(f"LLM | analyze_job_complete | SUCCESS | {execution_time:.2f}s | {tokens_used} tokens")
        
        return result
        
    except json.JSONDecodeError as e:
        execution_time = time.time() - start_time
        error_msg = f"JSON parsing error: {str(e)}"
        
        log_llm_call("analyze_job_complete", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | analyze_job_complete | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {
            "title": "Unknown Position",
            "company": "Unknown Company",
            "visa_sponsorship": None,
            "visa_analysis": "Unable to analyze",
            "match_percentage": 0,
            "match_analysis": "Unable to analyze"
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        log_llm_call("analyze_job_complete", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | analyze_job_complete | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {
            "title": "Unknown Position",
            "company": "Unknown Company",
            "visa_sponsorship": None,
            "visa_analysis": "Unable to analyze",
            "match_percentage": 0,
            "match_analysis": "Unable to analyze"
        }


def generate_cover_letter(resume: str, template: str, job_description: str, 
                         job_title: str, company: str) -> dict:
    """Generate personalized cover letter"""
    start_time = time.time()
    
    # Truncate long texts
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
        
        # For cover letter return just text (not JSON)
        # Log success
        log_llm_call("generate_cover_letter", "success", execution_time, tokens_used)
        logger.info(f"LLM | generate_cover_letter | SUCCESS | {execution_time:.2f}s | {tokens_used} tokens")
        
        return {"cover_letter": result_text}
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        log_llm_call("generate_cover_letter", "error", execution_time, error_message=error_msg)
        logger.error(f"LLM | generate_cover_letter | ERROR | {execution_time:.2f}s | {error_msg}")
        
        return {"cover_letter": "Unable to generate cover letter"}

