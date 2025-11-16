# 🔍 Job Search Helper

A simple web application to track job applications, analyze visa sponsorship, match resumes, and generate personalized cover letters using AI.

## ✨ Features

- 📝 **Job Tracking**: Add and manage job applications with status tracking
- 🤖 **AI-Powered Extraction**: Automatically extract job title and company from descriptions
- 🌍 **Visa Sponsorship Detection**: Analyze job postings for visa sponsorship mentions
- 📊 **Resume Matching**: Calculate compatibility percentage between your resume and job requirements
- ✉️ **Cover Letter Generation**: Create personalized cover letters tailored to each job
- 📈 **Usage Statistics**: Monitor your OpenAI API usage and costs
- 📅 **Automatic Date Tracking**: Track application and response dates automatically

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key

### Installation

1. **Clone or download the project**

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here
```

5. **Create your resume and cover letter template**
```bash
# Edit templates/user_resume.txt with your resume
# Edit templates/cover_letter_base.txt with your cover letter template
```

6. **Run the application**
```bash
chmod +x run.sh
./run.sh
```

7. **Open in browser**
```
http://localhost:8000
```

## 📖 How to Use

### Adding a Job

1. Paste the job description in the form
2. **(Optional)** Fill in Title and Company manually
3. Click "Add Job"
4. **AI automatically analyzes everything in one go:**
   - Extracts job title and company (if not provided)
   - Checks visa sponsorship status (Yes/No/N/A)
   - Calculates resume match percentage
5. Results appear instantly in the table! ✨

**Visa Sponsorship Status:**
- **✓ Yes** - Sponsorship explicitly mentioned or offered
- **✗ No** - Explicitly states NO sponsorship (e.g., "must be authorized to work")
- **N/A** - No mention of sponsorship at all

### Working with Jobs

For each job, you can:

- **Click Job Title**: If a job URL is provided, the title becomes a clickable link (opens in new tab)
- **View Analysis**: See visa sponsorship and resume match automatically
- **Hover for Details**: Hover over visa/match badges to see detailed AI analysis
- **Generate Cover Letter**: Click "Cover Letter" to create a personalized letter
- **Update Status**: Change status from dropdown (new → applied → interview → offer/rejected)
- **Delete**: Remove unwanted jobs

### Filtering & Sorting

**Filters:**
- **Status**: Filter by job status (New, Applied, Interview, Offer, Rejected)
- **Visa**: Filter by sponsorship (Yes, No, N/A)
- **Match**: Filter by resume match percentage (≥80%, ≥60%, ≥40%, <40%)
- Multiple filters can be combined
- Filters are saved in browser (persist after page reload)
- Click "🔄 Reset Filters" to clear all

**Sorting:**
- Click any table header to sort by that column
- First click: ascending ▲
- Second click: descending ▼
- Works with all columns (Title, Company, Visa, Match, Status, Dates)

### Status Workflow

- **new**: Just added
- **applied**: You've applied (sets `applied_date` automatically)
- **interview**: Interview scheduled
- **offer**: Got an offer (calculates `days_to_response`)
- **rejected**: Application rejected (calculates `days_to_response`)

### Viewing Statistics

Click "📈 Statistics" in the header to see:
- Total API calls made
- Tokens consumed
- Estimated costs
- Breakdown by function

## 📁 Project Structure

```
JobSearchHelper/
├── app/
│   ├── main.py              # FastAPI application & all endpoints
│   ├── models.py            # SQLAlchemy models (Job, LLMLog)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── database.py          # Database connection & session
│   ├── config.py            # Configuration & environment variables
│   ├── prompts.py           # LLM prompts
│   ├── llm.py               # OpenAI integration functions
│   └── static/
│       ├── index.html       # Main page
│       ├── stats.html       # Statistics page
│       ├── app.js           # Frontend logic
│       ├── stats.js         # Statistics page logic
│       └── style.css        # Styles
├── templates/
│   ├── user_resume.txt      # Your resume (customize this!)
│   └── cover_letter_base.txt  # Your base cover letter template
├── data/
│   └── jobs.db              # SQLite database (created automatically)
├── doc/
│   ├── idea.md              # Project idea and concept
│   └── tasklist.md          # Development task list
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Example environment file
├── requirements.txt         # Python dependencies
├── run.sh                   # Startup script
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./data/jobs.db
```

### Application Settings

Edit `app/config.py` for:
- **OpenAI model settings**: Model, temperature, max tokens
- **Token limits**: Text length limits for job descriptions and resumes
- **Cost tracking**: Cost per 1K tokens for statistics

## 💡 Tips

1. **Resume**: Keep `templates/user_resume.txt` updated with your latest experience
2. **Cover Letter Template**: Use `[CUSTOM_CONTENT]` placeholder in your base template - AI will replace it with job-specific content
3. **Job Descriptions**: Longer, more detailed descriptions give better AI analysis
4. **Costs**: Check `/stats` regularly to monitor OpenAI usage and costs
5. **Backup**: Your data is in `data/jobs.db` - back it up regularly
6. **Token Optimization**: The app uses a single API call for all analysis (~60% token savings vs. separate requests)

## 🐛 Troubleshooting

### "OpenAI API error"
- Check your API key in `.env`
- Ensure you have credits in your OpenAI account
- Verify the API key is valid

### "Database error"
- Delete `data/jobs.db` and restart (will reset all data)
- Check file permissions on `data/` directory

### "Template file not found"
- Make sure `templates/user_resume.txt` exists
- Make sure `templates/cover_letter_base.txt` exists
- Check file paths are correct

### Page not loading
- Ensure virtual environment is activated
- Check if port 8000 is available
- Look at console logs for errors

## 📝 Development Principles

This project follows **KISS (Keep It Simple, Stupid)** principles:
- ✅ Simple, flat structure
- ✅ All endpoints in one file
- ✅ Minimal dependencies
- ✅ No over-engineering
- ✅ MVP-first approach
- ✅ Synchronous LLM calls (except FastAPI endpoints)
- ✅ Console logging only
- ✅ Single-user SQLite database

## 🚀 Future Improvements

After MVP validation, potential enhancements:
- 🔐 Authentication for multi-user support
- 📤 Export to CSV/PDF
- 📧 Email notifications
- 🔗 Job board integrations (LinkedIn, Indeed, etc.)
- 🔍 Advanced filtering and search
- 📊 Analytics dashboard
- 🔄 Automatic status updates
- 💾 Cloud backup

## 📊 Technology Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML, Vanilla JavaScript, CSS
- **AI**: OpenAI API (GPT-3.5-turbo)
- **Server**: Uvicorn (ASGI server)

## 📄 License

MIT License - feel free to use and modify for your personal job search!

## 🤝 Contributing

This is a personal MVP project. Feel free to fork and customize for your needs!

## 📚 Documentation

- `doc/idea.md` - Original project idea
- `doc/tasklist.md` - Development progress and task list
- `.cursor/rules/` - Code conventions and workflow rules

---

**Built with ❤️ for job seekers**

Made with: Python | FastAPI | SQLite | Vanilla JavaScript | OpenAI API

