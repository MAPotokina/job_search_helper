"""
Промпты для LLM функций
"""

PROMPTS = {
    "analyze_job_complete": """Analyze the following job description and provide a comprehensive analysis.
Extract job information, analyze visa sponsorship, and calculate resume match.

Return ONLY a valid JSON object with this exact format:
{{
    "title": "job title here",
    "company": "company name here",
    "visa_sponsorship": true/false/null,
    "visa_analysis": "brief explanation",
    "match_percentage": 75,
    "match_analysis": "brief explanation"
}}

IMPORTANT for visa_sponsorship field:
- Use `true` ONLY if sponsorship is explicitly mentioned or offered
- Use `false` ONLY if it explicitly states NO sponsorship (e.g., "must be authorized to work", "no visa sponsorship")
- Use `null` if there is NO mention of sponsorship at all

Job Description:
{job_description}

Resume:
{resume}
""",
    
    "extract_job_info": """You are a job description analyzer. Extract the job title and company name from the following job description.

Return ONLY a valid JSON object with this exact format:
{{"title": "job title here", "company": "company name here"}}

If you cannot find the information, use:
{{"title": "Unknown Position", "company": "Unknown Company"}}

Job Description:
{job_description}
""",
    
    "visa_sponsorship": """Analyze this job description and determine if visa sponsorship is offered.

Return ONLY a valid JSON object with this exact format:
{{"has_sponsorship": true/false, "analysis": "brief explanation"}}

Job Description:
{job_description}
""",
    
    "resume_match": """Compare this resume with the job requirements and provide a match percentage.

Return ONLY a valid JSON object with this exact format:
{{"match_percentage": 75, "analysis": "explanation of the match"}}

Resume:
{resume}

Job Description:
{job_description}
""",
    
    "cover_letter": """Generate a personalized cover letter based on the resume, base template, and job description.

IMPORTANT: Return ONLY the cover letter text, no JSON, no markdown, no extra formatting.

Resume:
{resume}

Base Template:
{template}

Job Title: {job_title}
Company: {company}

Job Description:
{job_description}

Generate a professional cover letter that highlights relevant skills from the resume that match the job requirements.
"""
}

