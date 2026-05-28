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