import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def parse_job_description(job_description: str):

    prompt = f"""
    Extract the following details from this job description.

    Return ONLY valid JSON.
    Do not add markdown.
    Do not use triple backticks.

    {{
      "skills": [],
      "responsibilities": [],
      "experience_level": "",
      "keywords": []
    }}

    Job Description:
    {job_description}
    """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    response_text = completion.choices[0].message.content.strip()

    # Remove markdown code blocks if present
    response_text = re.sub(r"```json|```", "", response_text).strip()

    try:
        return json.loads(response_text)

    except Exception as e:
        return {
            "error": "Failed to parse response",
            "details": str(e),
            "raw_response": response_text
        }

def analyze_resume(resume_text: str, job_description: str):
    prompt = f"""
    Analyze the following resume against the job description.
    Provide a match percentage (0 to 100) indicating how well the candidate's profile matches the job requirements.
    List key strengths of the candidate that align with the role.
    List specific, actionable improvement suggestions for the resume to better target this specific role.

    Return ONLY valid JSON.
    Do not add markdown formatting.
    Do not use triple backticks.

    {{
      "match_percentage": 0,
      "strengths": ["string"],
      "improvements": ["string"]
    }}

    Job Description:
    {job_description}

    Resume:
    {resume_text}
    """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    response_text = completion.choices[0].message.content.strip()
    response_text = re.sub(r"```json|```", "", response_text).strip()

    try:
        return json.loads(response_text)
    except Exception as e:
        return {
            "error": "Failed to parse response",
            "details": str(e),
            "raw_response": response_text
        }

def generate_cover_message(resume_text: str, job_description: str, company_name: str, role: str):
    prompt = f"""
    Generate a highly customized, compelling, and professional cover letter / cold outreach message for a job application.
    The message should highlight relevant experience from the candidate's resume that matches the job description.
    Keep it concise, engaging, and professional (approximately 200-300 words).

    Company Name: {company_name}
    Role: {role}

    Return ONLY valid JSON with a single key "cover_message".
    Do not add markdown formatting.
    Do not use triple backticks.

    {{
      "cover_message": "string"
    }}

    Job Description:
    {job_description}

    Resume:
    {resume_text}
    """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    response_text = completion.choices[0].message.content.strip()
    response_text = re.sub(r"```json|```", "", response_text).strip()

    try:
        return json.loads(response_text)
    except Exception as e:
        return {
            "error": "Failed to parse response",
            "details": str(e),
            "raw_response": response_text
        }