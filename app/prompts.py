"""
Промпты для LLM функций
"""

PROMPTS = {
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

Return ONLY a valid JSON object with this exact format:
{{"cover_letter": "the complete cover letter text here"}}

Resume:
{resume}

Base Template:
{template}

Job Title: {job_title}
Company: {company}

Job Description:
{job_description}
"""
}

