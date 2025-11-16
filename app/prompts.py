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
    "visa_analysis": "text string with detailed explanation",
    "match_percentage": calculated match percentage,
    "match_analysis": "text string with structured analysis"
}}

CRITICAL JSON FORMATTING:
- visa_analysis and match_analysis MUST be plain text strings, NOT nested objects or arrays!
- Use \\n (double backslash n) for line breaks inside strings, NOT actual newline characters
- Make sure all string values are properly escaped for JSON

CRITICAL for visa_sponsorship field - BE VERY STRICT:
- Use `true` ONLY if the job posting EXPLICITLY STATES they offer/provide visa sponsorship (words like "visa sponsorship available", "will sponsor")
- Use `false` ONLY if it EXPLICITLY STATES they do NOT sponsor (e.g., "must be authorized to work", "no visa sponsorship", "citizenship required")
- Use `null` in ALL OTHER CASES - even if you think the company could afford it or typically sponsors. If it's not explicitly mentioned, it's `null`

DO NOT infer true/false from company size or industry - ONLY from explicit statements in the job posting!

CRITICAL for visa_analysis field - YOU MUST PROVIDE ALL 4 SECTIONS BELOW:

SECTION 1 - Direct Statement: [What job explicitly says about sponsorship OR "The job posting does not mention visa sponsorship."]\\n\\n

SECTION 2 - Company Analysis: You MUST research the company from job description and write: "[Company name] is a [startup/small/medium-sized/large enterprise] company in the [specific industry] sector. Companies in this industry [typically do/rarely/sometimes] sponsor H1B visas because [specific reason]. Based on the job description, this company appears to [have global presence/be local/have international operations/etc]."\\n\\n

SECTION 3 - Sponsorship Likelihood: You MUST pick ONE rating and explain: "[Very Likely/Likely/Uncertain/Unlikely/Very Unlikely]\\nReasoning: [Write 2-3 FULL sentences explaining WHY. Consider: company size and budget, industry sponsorship norms, job seniority level, salary indicators, company's global footprint, market position, tech stack requirements, etc.]"\\n\\n

SECTION 4 - Key Indicators Found: You MUST list 2-4 specific signals from job description: "[signal 1]; [signal 2]; [signal 3]; [signal 4]"

EVEN IF visa sponsorship is not mentioned, you MUST write detailed Company Analysis, Sponsorship Likelihood with reasoning, and Key Indicators. DO NOT STOP after "not mentioned" - that's only Section 1!

EXAMPLE of good visa_analysis (note the \\n\\n for line breaks):
"Direct Statement: The job posting does not mention visa sponsorship.\\n\\nCompany Analysis: EPAM Systems is a large enterprise (50,000+ employees) company in the IT consulting and software engineering sector. Companies in this industry typically do sponsor H1B visas because they compete globally for technical talent and have established immigration departments. Based on the job description, this company appears to have strong global presence with offices worldwide and regular international project work.\\n\\nSponsorship Likelihood: Very Likely\\nReasoning: As a Fortune 1000 company with extensive international operations, EPAM has both the financial resources and institutional infrastructure to handle visa sponsorships. Senior technical positions like this one are traditionally harder to fill domestically, making companies more willing to sponsor. The job's focus on cutting-edge technologies and lack of citizenship requirements are positive signals.\\n\\nKey Indicators Found: Global team collaboration mentioned; No citizenship or work authorization requirements stated; Senior-level position ($120K+ implied by responsibilities); Company's international reputation and multiple office locations; Technology stack suggests competitive compensation."

CRITICAL for match_analysis field - Return as a SINGLE TEXT STRING with clear formatting:

REQUIRED FORMAT (use \\n for line breaks in JSON):
"✅ STRENGTHS:\\n- [First strength - be specific]\\n- [Second strength]\\n- [Third strength]\\n- [Continue with all matching skills/experience]\\n\\n❌ GAPS:\\n- [First gap or missing skill]\\n- [Second gap]\\n- [Third gap]\\n- [Continue with all gaps]"

Be comprehensive - list ALL significant strengths and gaps. Use \\n (escaped newline) between bullets for JSON compatibility.

FINAL REMINDER: 
- visa_analysis MUST contain ALL 4 SECTIONS (Direct Statement, Company Analysis, Sponsorship Likelihood with reasoning, Key Indicators)
- match_analysis MUST contain both STRENGTHS and GAPS sections with multiple bullet points
- DO NOT write short/incomplete analysis - be thorough!

Job Description:
{job_description}

Resume:
{resume}
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

