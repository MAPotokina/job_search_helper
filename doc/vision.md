# Technical Vision - Job Search Helper

## 1. Technologies

### Backend
- **Python 3.10+** - main development language
- **FastAPI** - web framework (fast, simple, auto-documentation)
- **SQLite** - embedded database (zero configuration)
- **Pydantic** - data validation (built into FastAPI)

### Frontend
- **HTML + Vanilla JavaScript + CSS** - minimal stack without frameworks
- No bundlers (webpack, vite) at start

### LLM Integration
- **OpenAI API** (GPT-3.5-turbo to start) - job analysis and cover letter assistance
- **openai** (official Python library)

### Additional Libraries
- **SQLAlchemy** - ORM for database work
- **python-dotenv** - environment variable management
- **uvicorn** - ASGI server for FastAPI

### Development Tools
- **venv** - virtual environment (already configured)
- **requirements.txt** - dependency management

## 2. Development Principles

### Philosophy
- **KISS (Keep It Simple, Stupid)** - maximum simplicity in everything
- **MVP-first** - working prototype is more important than perfect code
- **Monolithic architecture** - everything in one application
- **No premature optimization** - optimize only real problems

### Technical Decisions
- **Single-user application** - no authentication system for MVP
- **Synchronous code** - async only in FastAPI endpoints where necessary
- **ORM (SQLAlchemy)** - for convenient database work, but without complex relationships
- **Minimal validation** - only critical checks via Pydantic
- **Straightforward structure** - simple modules, minimal abstractions

### What we DON'T do for MVP
- ❌ Authentication and authorization system
- ❌ Unit tests (will add later)
- ❌ CI/CD pipelines
- ❌ Docker and containerization
- ❌ Microservices architecture
- ❌ Caching
- ❌ Asynchronous task processing (Celery, etc.)

## 3. Project Structure

```
JobSearchHelper/
├── app/
│   ├── main.py              # FastAPI application, entry point
│   ├── database.py          # Database setup and SQLAlchemy
│   ├── models.py            # SQLAlchemy models (tables)
│   ├── schemas.py           # Pydantic schemas for API
│   ├── llm.py               # Work with OpenAI API
│   └── static/              # Static files for frontend
│       ├── index.html       # Main page
│       ├── style.css        # Styles
│       └── app.js           # Frontend logic
├── templates/
│   └── cover_letter_base.txt  # Base cover letter template for user
├── data/
│   └── jobs.db              # SQLite database (created automatically)
├── .env                     # Environment variables (OPENAI_API_KEY)
├── .env.example             # Example .env file
├── .gitignore               # Git exclusions
├── requirements.txt         # Python dependencies
├── idea.md                  # Project idea description
└── vision.md                # Technical design (this document)
```

### Structure Principles
- **Flat organization** - all modules at one level in `app/` folder
- **One file = one responsibility** - database, models, llm, schemas separate
- **Minimal nesting** - no subpackages like `routers/`, `services/`, `utils/`
- **Console logs** - no log files for MVP

## 4. Project Architecture

### Overall Scheme (3-tier architecture)

```
┌─────────────────────────────────────┐
│   Frontend (HTML/JS/CSS)            │  ← User's browser
│   - Add job form                    │
│   - Jobs list                       │
│   - Cover letter generation         │
└──────────────┬──────────────────────┘
               │ HTTP/JSON (REST API)
┌──────────────▼──────────────────────┐
│   FastAPI Application (main.py)     │
│   - REST endpoints (CRUD)           │
│   - Validation (Pydantic schemas)   │
│   - Static file serving             │
└──────┬────────────────────┬─────────┘
       │                    │
       │                    └──────────┐
       │                               │
┌──────▼──────────┐          ┌─────────▼────────┐
│  SQLAlchemy ORM │          │  LLM Service     │
│  (models.py)    │          │  (llm.py)        │
│  - Job model    │          │  - Sponsorship   │
│  - CRUD ops     │          │  - Cover letter  │
└──────┬──────────┘          └─────────┬────────┘
       │                               │
┌──────▼──────────┐          ┌─────────▼────────┐
│  SQLite DB      │          │  OpenAI API      │
│  (jobs.db)      │          │  (GPT-3.5)       │
└─────────────────┘          └──────────────────┘
```

### API Endpoints

**Static files:**
- `GET /` - main page (index.html)

**Job Management:**
- `GET /api/jobs` - get all jobs
- `POST /api/jobs` - add new job
- `GET /api/jobs/{id}` - get job by ID
- `PUT /api/jobs/{id}` - update job (including status)
- `DELETE /api/jobs/{id}` - delete job

**LLM Features:**
- `POST /api/extract-job-info` - extract title and company from description (automatic)
- `POST /api/analyze-sponsorship` - analyze job text for visa sponsorship
- `POST /api/analyze-match` - analyze resume-job match
- `POST /api/generate-cover-letter` - generate personalized cover letter

### Key Decisions
- **Monolith** - everything in one FastAPI application
- **REST API** - standard HTTP methods and JSON
- **Synchronous LLM calls** - user waits for response
- **Store cover letters in database** - for history and reuse
- **No middleware** - minimal request processing
- **No routers** - all endpoints in main.py

## 5. Data Model

### Table: `jobs`

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `title` | String(200) | Position title |
| `company` | String(200) | Company name |
| `job_url` | String(500) | Job listing URL |
| `job_description` | Text | Full job description |
| `has_visa_sponsorship` | Boolean (nullable) | Has sponsorship (null/true/false) |
| `sponsorship_analysis` | Text (nullable) | LLM analysis result |
| `resume_match_percentage` | Integer (nullable) | Resume match (0-100) |
| `match_analysis` | Text (nullable) | LLM explanation |
| `status` | String(50) | Application status (enum) |
| `cover_letter` | Text (nullable) | Generated cover letter |
| `applied_date` | DateTime (nullable) | Application submission date |
| `response_date` | DateTime (nullable) | Response received date |
| `days_to_response` | Integer (nullable) | Days to response (auto-calculated) |
| `created_at` | DateTime | Record creation date |
| `updated_at` | DateTime | Last update date |

### Enum: Status
- `new` - added to system, not applied yet
- `applied` - application submitted
- `interview` - invited to interview
- `offer` - received offer
- `rejected` - rejected

### User Files

```
templates/
  ├── cover_letter_base.txt  # Base cover letter template
  └── user_resume.txt         # User's resume (for analysis)
```

### Logic
- **days_to_response**: calculated automatically when `response_date` is set
- **resume_match_percentage**: filled on user request ("Analyze Match" button)
- **has_visa_sponsorship**: filled via LLM analysis of description text
- **cover_letter**: generated on request based on `user_resume.txt` + `cover_letter_base.txt` + `job_description`

## 6. Working with LLM

### LLM Functions

#### 1. Visa Sponsorship Analysis
**Function:** `analyze_visa_sponsorship(job_description: str)`
- **Input:** job description text (max 5000 characters)
- **Output:** `{"has_sponsorship": bool, "analysis": str}`
- **Model:** GPT-3.5-turbo
- **Prompt:** from config file

#### 2. Resume Match Analysis
**Function:** `analyze_resume_match(resume: str, job_description: str)`
- **Input:** resume + job description (max 5000 characters each)
- **Output:** `{"match_percentage": int, "analysis": str}`
- **Model:** GPT-3.5-turbo
- **Prompt:** from config file

#### 3. Cover Letter Generation
**Function:** `generate_cover_letter(resume: str, template: str, job_description: str, job_title: str, company: str)`
- **Input:** resume + base template + job description + position title + company
- **Output:** `{"cover_letter": str}`
- **Model:** GPT-3.5-turbo
- **Prompt:** from config file

#### 4. Extract Job Info (automatic extraction)
**Function:** `extract_job_info(job_description: str)`
- **Input:** job description text
- **Output:** `{"title": str, "company": str}`
- **Model:** GPT-3.5-turbo
- **Prompt:** from config file
- **Usage:** automatically when adding new job

### Technical Parameters

```python
# OpenAI API settings
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.3  # More deterministic responses
MAX_TOKENS = 1000
TIMEOUT = 30  # seconds

# Limits
MAX_JOB_DESCRIPTION_LENGTH = 5000  # characters
MAX_RESUME_LENGTH = 5000  # characters
```

### Prompt Configuration

**File:** `app/prompts.py`

```python
PROMPTS = {
    "visa_sponsorship": "...",
    "resume_match": "...",
    "cover_letter": "...",
    "extract_job_info": "..."
}
```

### Error Handling
- **API unavailable** → return HTTP 503 with error message
- **Rate limit** → return HTTP 429 with message
- **Timeout** → return HTTP 504
- **Long text** → automatically trim to limit before sending
- **No retry** → one attempt, immediately return error to user on failure

## 7. LLM Monitoring

### Table: `llm_logs`

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `function_name` | String(100) | Function name (visa_sponsorship, resume_match, cover_letter) |
| `status` | String(50) | Execution status (success, error) |
| `execution_time` | Float | Execution time in seconds |
| `tokens_used` | Integer (nullable) | Number of tokens used |
| `error_message` | Text (nullable) | Error message |
| `created_at` | DateTime | Request timestamp |

### Logging

**Console log format:**
```
[2025-11-16 10:30:45] LLM | analyze_visa_sponsorship | SUCCESS | 2.3s | 150 tokens
[2025-11-16 10:31:12] LLM | generate_cover_letter | ERROR | 0.5s | OpenAI timeout
[2025-11-16 10:32:00] LLM | analyze_resume_match | SUCCESS | 3.1s | 280 tokens
```

**What we log:**
- Timestamp
- Function name
- Status (SUCCESS/ERROR)
- Execution time
- Tokens used (if success)
- Error text (if error)

### Statistics Page

**URL:** `GET /stats` or separate UI section

**Display:**
- Total number of LLM requests
- Successful / with errors
- Total tokens used
- Estimated cost (tokens × GPT-3.5-turbo price)
- Breakdown by function (how many times each)
- Average execution time

### Cost Calculation

```python
# Approximate GPT-3.5-turbo prices (November 2025)
COST_PER_1K_TOKENS = 0.002  # $0.002 per 1K tokens

total_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS
```

### Statistics API Endpoint
- `GET /api/stats` - get LLM usage statistics

## 8. Usage Scenarios

### Scenario 1: Adding New Job
1. User opens main page
2. Pastes **only URL and job description** into form
3. Clicks "Add Job"
4. **System automatically extracts via LLM:**
   - Position title (title)
   - Company name (company)
5. Saves to database with status "new"
6. Job appears in list with auto-filled fields

### Scenario 2: Visa Sponsorship Analysis
1. User sees job in list
2. Clicks "Check Sponsorship" button
3. System sends description to LLM
4. Receives result (yes/no + explanation)
5. Updates `has_visa_sponsorship` and `sponsorship_analysis` in database
6. Shows result to user (badge or icon)

### Scenario 3: Resume Match Check
1. User clicks "Analyze Match" on specific job
2. System reads `templates/user_resume.txt`
3. Sends resume + job description to LLM
4. Receives percentage (0-100) + explanation
5. Saves `resume_match_percentage` and `match_analysis` to database
6. Shows percentage and explanation

### Scenario 4: Cover Letter Generation
1. User clicks "Generate Cover Letter"
2. System reads:
   - `templates/user_resume.txt`
   - `templates/cover_letter_base.txt`
3. Sends to LLM along with job description, title and company
4. Receives personalized cover letter
5. Saves to `cover_letter` field in database
6. Shows letter in modal window (can copy/download)

### Scenario 5: Application Status Update
1. User changes status via dropdown (new → applied → interview → offer/rejected)
2. **When changing to "applied":**
   - System automatically sets `applied_date = today()`
   - Field remains editable (can change date)
3. **When changing to "offer" or "rejected":**
   - System automatically sets `response_date = today()`
   - Automatically calculates `days_to_response = response_date - applied_date`
   - Field `response_date` remains editable
4. Changes saved to database

### Scenario 6: View Statistics
1. User opens `/stats` page or Statistics section
2. Sees overall LLM usage statistics:
   - Number of requests
   - Tokens used
   - Estimated cost
   - Breakdown by function
3. Can use for cost control

## 9. Deployment

### Local Run (MVP)

**Approach:** Simple local run on developer's machine

**Requirements:**
- Python 3.10+
- Virtual environment (venv)
- OpenAI API key

**Startup script:** `run.sh`
```bash
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with OPENAI_API_KEY"
    exit 1
fi

# Start FastAPI application
echo "Starting Job Search Helper..."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Access:** `http://localhost:8000`

### README Instructions

**Startup steps:**
1. Clone repository
2. Create `.env` file with `OPENAI_API_KEY=your_key_here`
3. Activate venv: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `./run.sh` or `uvicorn app.main:app --reload`
6. Open browser: `http://localhost:8000`

**First run:**
- Create file `templates/user_resume.txt` with your resume
- Create file `templates/cover_letter_base.txt` with base template
- Database `data/jobs.db` will be created automatically

### What we DON'T do for MVP
- ❌ Docker/containerization
- ❌ CI/CD pipelines
- ❌ Production WSGI server (Gunicorn)
- ❌ Reverse proxy (Nginx)
- ❌ HTTPS/SSL
- ❌ Remote access
- ❌ Multi-user mode

### Stop Application
- `Ctrl+C` in terminal where uvicorn is running

## 10. Configuration Approach

### Configuration Structure

**Principle:** Separate secrets, settings and prompts into different files

### File: `.env` (secret data)
```env
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=sqlite:///./data/jobs.db
```

- **NOT committed to git** (in .gitignore)
- Only API keys and sensitive data

### File: `.env.example` (template for users)
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./data/jobs.db
```

- **Committed to git** as example
- Helps other developers set up environment

### File: `app/config.py` (technical settings)
```python
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1000
OPENAI_TIMEOUT = 30  # seconds

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobs.db")

# Text length limits
MAX_JOB_DESCRIPTION_LENGTH = 5000  # characters
MAX_RESUME_LENGTH = 5000  # characters

# Cost for statistics calculation
COST_PER_1K_TOKENS = 0.002  # $0.002 per 1K tokens (GPT-3.5-turbo)
```

### File: `app/prompts.py` (LLM prompts)
```python
PROMPTS = {
    "extract_job_info": """
        Extract the job title and company name from this job description.
        Return JSON: {"title": "...", "company": "..."}
        """,
    
    "visa_sponsorship": """
        Analyze this job description and determine if visa sponsorship is offered.
        Return JSON: {"has_sponsorship": true/false, "analysis": "..."}
        """,
    
    "resume_match": """
        Compare this resume with the job requirements.
        Return JSON: {"match_percentage": 0-100, "analysis": "..."}
        """,
    
    "cover_letter": """
        Generate a personalized cover letter based on the resume,
        base template, and job description.
        Return JSON: {"cover_letter": "..."}
        """
}
```

### Approach Advantages
- **Secrets separate** - `.env` will never get into git
- **Settings centralized** - all parameters in `config.py`
- **Prompts editable** - easy to change without searching through code
- **Simplicity** - no complex config systems, YAML, JSON files

## 11. Logging Approach

### Principle

**Minimal logging to console** - no files, no rotation, no complex systems

### What We Log

#### 1. Application Startup
```
[2025-11-16 10:00:00] INFO | Application started on http://127.0.0.1:8000
[2025-11-16 10:00:00] INFO | Database connected: sqlite:///./data/jobs.db
[2025-11-16 10:00:00] INFO | OpenAI API configured
```

#### 2. API Requests (main operations)
```
[2025-11-16 10:01:23] INFO | POST /api/jobs | 201 Created | Job ID: 42
[2025-11-16 10:02:15] INFO | GET /api/jobs | 200 OK | 15 jobs returned
[2025-11-16 10:03:00] INFO | DELETE /api/jobs/42 | 204 No Content
```

#### 3. LLM Calls (detailed)
```
[2025-11-16 10:03:45] LLM | extract_job_info | SUCCESS | 2.1s | 120 tokens
[2025-11-16 10:04:12] LLM | analyze_visa_sponsorship | SUCCESS | 3.5s | 180 tokens
[2025-11-16 10:05:00] LLM | generate_cover_letter | SUCCESS | 5.2s | 450 tokens
[2025-11-16 10:06:30] LLM | analyze_resume_match | ERROR | 0.5s | OpenAI timeout
```

#### 4. Errors (everything in detail)
```
[2025-11-16 10:07:00] ERROR | Database error: unable to open database file
[2025-11-16 10:08:15] ERROR | OpenAI API error: Rate limit exceeded
[2025-11-16 10:09:30] ERROR | File not found: templates/user_resume.txt
```

### Technical Details

**Library:** Standard Python `logging` module

**Configuration:**
```python
import logging

# Simple configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
```

**Log Levels:**
- `INFO` - normal operation (startup, API calls, LLM success)
- `ERROR` - errors (API errors, DB errors, file errors)
- `DEBUG` - disabled for MVP (can enable for debugging)

### What We DON'T Log
- ❌ Full job descriptions text (too long)
- ❌ API keys and secrets
- ❌ User resume content
- ❌ Full cover letter texts
- ❌ SQL queries (not needed for MVP)

### Where We Log
- ✅ **Console (stdout)** - only output
- ❌ Files - not used
- ❌ External services (Sentry, CloudWatch) - not used

### Usage Example in Code
```python
from app.config import logger

# Successful operation
logger.info("Job created successfully", extra={"job_id": job.id})

# Error
logger.error(f"Failed to call OpenAI API: {error_message}")
```

---

## Conclusion

This document describes **Minimum Viable Product (MVP)** for Job Search Helper - a simple, functional application to test the idea.

### Key MVP Principles
- ✅ **KISS** - maximum simplicity
- ✅ **Monolith** - everything in one place
- ✅ **Single-user** - one user, local run
- ✅ **Quick start** - from zero to working application in minimal time
- ✅ **No over-engineering** - no unnecessary technologies and patterns

### Development Readiness
Document contains everything necessary to start development:
- Technology stack defined
- Architecture designed
- Data model described
- Usage scenarios detailed
- Implementation approach agreed

### Next Steps
1. Create project structure
2. Set up environment (requirements.txt, .env)
3. Implement database and models
4. Implement LLM integration
5. Create API endpoints
6. Develop simple web interface
7. Testing and launch

**Document is ready to use as technical specification for development!**


