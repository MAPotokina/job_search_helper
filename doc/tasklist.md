# Development Task List - Job Search Helper

## 📊 Progress Report

| Iteration | Name | Status | Completion Date | Test Passed |
|-----------|------|--------|-----------------|-------------|
| 0 | Project Setup | ✅ Done | 2025-11-16 | ✅ |
| 1 | Database & Models | ✅ Done | 2025-11-16 | ✅ |
| 2 | Basic CRUD API | ✅ Done | 2025-11-16 | ✅ |
| 3 | Frontend UI | ✅ Done | 2025-11-16 | ✅ |
| 4 | LLM: Extract Job Info | ✅ Done | 2025-11-16 | ✅ |
| 5 | LLM: Visa Sponsorship | ✅ Done | 2025-11-16 | ✅ |
| 6 | LLM: Resume Match | ✅ Done | 2025-11-16 | ✅ |
| 7 | LLM: Cover Letter | ✅ Done | 2025-11-16 | ✅ |
| 8 | Statistics & Monitoring | ✅ Done | 2025-11-16 | ✅ |
| 9 | Polish & Production Ready | ✅ Done | 2025-11-16 | ✅ |
| 10 | Token Optimization | ✅ Done | 2025-11-16 | ✅ |
| 11 | Tooltips for Analysis | ✅ Done | 2025-11-16 | ✅ |
| 12 | Sorting & Filters | ✅ Done | 2025-11-16 | ✅ |

**Status Legend:**
- ⏳ Pending - not started
- 🚧 In Progress - in progress
- ✅ Done - completed
- ❌ Failed - failed

---

## Iteration 0: Project Setup 🏗️

**Goal:** Run empty FastAPI application

### Tasks
- [x] Create folder structure (`app/`, `data/`, `templates/`)
- [x] Create `requirements.txt` with dependencies
- [x] Create `.env.example` and `.env` with `OPENAI_API_KEY`
- [x] Create `.gitignore`
- [x] Create `app/config.py` with settings
- [x] Create `app/main.py` with minimal FastAPI
- [x] Create `run.sh` startup script

### Test
```bash
./run.sh
# Open http://localhost:8000
# Should return JSON: {"message": "Job Search Helper API"}
```

---

## Iteration 1: Database & Models 💾

**Goal:** Create database and models

### Tasks
- [x] Create `app/database.py` (SQLAlchemy setup)
- [x] Create `app/models.py` with `Job` and `LLMLog` models
- [x] Add automatic table creation on startup
- [x] Create endpoint `GET /api/health` to check database

### Test
```bash
./run.sh
# GET http://localhost:8000/api/health
# Should return: {"status": "ok", "database": "connected"}
# Verify that file data/jobs.db was created
```

---

## Iteration 2: Basic CRUD API 📝

**Goal:** CRUD operations for jobs (without LLM)

### Tasks
- [x] Create `app/schemas.py` with Pydantic schemas
- [x] Implement `POST /api/jobs` (create job manually)
- [x] Implement `GET /api/jobs` (list all jobs)
- [x] Implement `GET /api/jobs/{id}` (single job)
- [x] Implement `PUT /api/jobs/{id}` (update)
- [x] Implement `DELETE /api/jobs/{id}` (delete)
- [x] Add automatic date filling on status change

### Test
```bash
# Create job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"title":"Python Dev","company":"ACME","job_url":"http://...","job_description":"...","status":"new"}'

# Get list
curl http://localhost:8000/api/jobs

# Update status to "applied"
curl -X PUT http://localhost:8000/api/jobs/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"applied"}'

# Verify that applied_date was filled automatically
```

---

## Iteration 3: Frontend UI 🎨

**Goal:** Simple web interface for managing jobs

### Tasks
- [x] Create `app/static/index.html` (main page)
- [x] Create `app/static/style.css` (basic styles)
- [x] Create `app/static/app.js` (UI logic)
- [x] Add job form (all fields manual for now)
- [x] Table with jobs list
- [x] Edit and delete buttons
- [x] Dropdown for status change
- [x] Configure StaticFiles in FastAPI

### Test
```bash
./run.sh
# Open http://localhost:8000
# Add several jobs through UI
# Change statuses
# Delete a job
# Verify everything works through UI
```

---

## Iteration 4: LLM - Extract Job Info 🤖

**Goal:** Automatic extraction of title and company from description

### Tasks
- [x] Create `app/prompts.py` with prompts
- [x] Create `app/llm.py` with `extract_job_info()` function
- [x] Create endpoint `POST /api/extract-job-info`
- [x] Add logging to `llm_logs` table
- [x] Integrate into UI: autofill when adding job
- [x] LLM error handling

### Test
```bash
# In UI paste only job_url and description
# Click "Add Job"
# Verify that title and company were filled automatically
# Verify that console has LLM call log
# Verify that llm_logs table has new entry
```

---

## Iteration 5: LLM - Visa Sponsorship 🌍

**Goal:** Visa sponsorship analysis via LLM

### Tasks
- [x] Add `visa_sponsorship` prompt to `prompts.py`
- [x] Add `analyze_visa_sponsorship()` function to `llm.py`
- [x] Create endpoint `POST /api/analyze-sponsorship`
- [x] Add "Check Sponsorship" button to UI
- [x] Display result (badge or icon)
- [x] Save result to database

### Test
```bash
# In UI click "Check Sponsorship" on a job
# Verify that badge appeared (Yes/No/Unknown)
# Verify that has_visa_sponsorship was filled in database
# Check console logs
```

---

## Iteration 6: LLM - Resume Match 📊

**Goal:** Resume-job matching analysis

### Tasks
- [x] Create `templates/user_resume.txt` with sample resume
- [x] Add `resume_match` prompt to `prompts.py`
- [x] Add `analyze_resume_match()` function to `llm.py`
- [x] Create endpoint `POST /api/analyze-match`
- [x] Add "Analyze Match" button to UI
- [x] Display match percentage and explanation

### Test
```bash
# Create templates/user_resume.txt with test resume
# In UI click "Analyze Match" on a job
# Verify that percentage is displayed (0-100%)
# Verify that explanation is shown
# Verify that it was saved to database
```

---

## Iteration 7: LLM - Cover Letter ✉️

**Goal:** Generate personalized cover letter

### Tasks
- [x] Create `templates/cover_letter_base.txt` with base template
- [x] Add `cover_letter` prompt to `prompts.py`
- [x] Add `generate_cover_letter()` function to `llm.py`
- [x] Create endpoint `POST /api/generate-cover-letter`
- [x] Add "Generate Cover Letter" button to UI
- [x] Modal window to display letter
- [x] Copy to clipboard button

### Test
```bash
# Create templates/cover_letter_base.txt with template
# In UI click "Generate Cover Letter" on a job
# Verify that modal window opened with letter
# Copy letter via button
# Verify that letter was saved to database
```

---

## Iteration 8: Statistics & Monitoring 📈

**Goal:** LLM usage statistics page

### Tasks
- [x] Create endpoint `GET /api/stats`
- [x] Calculate statistics from `llm_logs` table
- [x] Create `/stats` page in UI
- [x] Display total number of requests
- [x] Display tokens used
- [x] Display estimated cost
- [x] Breakdown by function
- [x] Statistics chart or table

### Test
```bash
# Open http://localhost:8000/stats
# Verify that statistics are displayed
# Verify token counting
# Verify cost calculation
# Verify breakdown by request type
```

---

## Iteration 9: Polish & Production Ready 🎯

**Goal:** Final polish and production readiness

### Tasks
- [x] Improve UI/UX (styles, responsiveness)
- [x] Add handling for all edge cases
- [x] Add loading indicators for LLM requests
- [x] Add toast notifications for success/errors
- [x] Check all error messages
- [x] Update README.md with instructions
- [x] Final testing of all scenarios
- [x] Create example templates/ files

### Test
```bash
# Full test cycle:
# 1. Add 5 jobs (auto-extract info)
# 2. Check sponsorship on all
# 3. Analyze match on 3 jobs
# 4. Generate cover letter for 2 jobs
# 5. Change statuses (new → applied → interview → offer)
# 6. Verify automatic date filling
# 7. Open statistics and check data
# 8. Everything should work without errors
```

---

## 🎉 Done!

After completing all iterations you will have a fully working MVP of Job Search Helper.

**Next steps after MVP:**
- Collect feedback from real usage
- Identify what to improve
- Prioritize new features based on experience

---

## Iteration 10: Token Optimization 💰

**Goal:** Combine LLM analyses to save tokens

### Tasks
- [x] Create comprehensive `analyze_job_complete` prompt
- [x] Add `analyze_job_complete()` function to `llm.py`
- [x] Update `POST /api/jobs` endpoint for automatic analysis
- [x] Remove old endpoints (extract-job-info, analyze-sponsorship, analyze-match)
- [x] Update frontend - remove "Check Visa" and "Analyze Match" buttons
- [x] Add "N/A" badge for undefined sponsorship
- [x] Update logic: null = N/A, false = explicitly no, true = explicitly yes
- [x] Update README.md with new instructions
- [x] Test automatic analysis

### Test
```bash
# Open http://localhost:8000
# Add job with description
# Verify that the following were filled automatically:
#  - Title and Company (if not specified)
#  - Visa Sponsorship (Yes/No/N/A)
#  - Resume Match (%)
# Check statistics - should have one analyze_job_complete function
# Check logs - one LLM call instead of three
```

**Savings:** ~60% tokens (1 request instead of 3 separate)

---

## Iteration 11: Tooltips for Analysis 💬

**Goal:** Display detailed analysis on hover

### Tasks
- [x] Add CSS for tooltips with animation
- [x] Update JavaScript to add tooltip-wrapper
- [x] Add tooltip for Visa Sponsorship badge (show sponsorship_analysis)
- [x] Add tooltip for Resume Match badge (show match_analysis)
- [x] Adapt for mobile devices
- [x] Fix tooltip clipping at table edge (overflow: visible)
- [x] Improve visa analysis prompt - add company analysis and likelihood
- [x] Remove unused prompts (extract_job_info, visa_sponsorship, resume_match)
- [x] Remove unused functions from llm.py
- [x] Fix strict visa_sponsorship logic (only on explicit mention)
- [x] Improve visa_analysis - clear structure with mandatory likelihood assessment
- [x] Improve match_analysis - lists of strengths and weaknesses
- [x] Increase OPENAI_MAX_TOKENS to 1500 for detailed responses
- [x] Fix error saving dict to database (convert to JSON string)
- [x] Strengthen prompt for mandatory detailed visa analysis (4 sections)
- [x] Add line breaks in tooltip for readability
- [x] Increase tooltip width to 400px and add max-height
- [x] Make prompt MAXIMALLY strict with mandatory requirements
- [x] Add concrete example of good visa_analysis
- [x] Increase OPENAI_TEMPERATURE to 0.5 for more creative analysis
- [x] Fix JSON parsing error - require \\n instead of real newlines
- [x] Add fallback handling for control characters in llm.py
- [x] Update examples with correct JSON format (\\n\\n)
- [x] Rewrite prompt with explicit SECTION 1-4 and "YOU MUST" imperatives
- [x] Add "DO NOT STOP after 'not mentioned'" warning
- [x] Add FINAL REMINDER at end of prompt
- [x] FIX fallback in llm.py - convert newlines to \\n, not to spaces
- [x] Add detailed logging in llm.py (length, preview)
- [x] Add detailed logging in main.py before saving to database
- [x] Test with fixed fallback and logs

### Test
```bash
# Open http://localhost:8000
# Add job with description
# Hover over "✓ Yes" or "✗ No" or "N/A" badge for visa sponsorship
# Tooltip with detailed analysis should appear
# Hover over match percentage (e.g. "75%")
# Tooltip with match analysis should appear
# Test on mobile (tooltip should be adapted)
```

**UX Improvement:** User sees details without extra clicks!

---

## Iteration 12: Sorting & Filters 🔍

**Goal:** Add sorting and filtering capability for jobs table

### Tasks
- [x] Add UI for filters (status, visa, match %)
- [x] Add UI for sorting (clickable column headers)
- [x] Implement client-side filtering in JavaScript
- [x] Implement client-side sorting in JavaScript
- [x] Add active sorting indicators (arrows ▲▼)
- [x] Save filters/sorting state to localStorage
- [x] Add "Reset Filters" button
- [x] Adapt for mobile devices

### Test
```bash
# Open http://localhost:8000
# Add several jobs with different statuses, visa, match %
# Test filtering by each parameter
# Test sorting by each column (A-Z, Z-A)
# Test combination of filters + sorting
# Test "Reset Filters"
```

**UX Improvement:** Quick search for needed jobs in a large list!

---

**Documentation:**
- [vision.md](../vision.md) - technical vision
- [conventions.md](../conventions.md) - development rules
- [idea.md](../idea.md) - idea description

