"""\nAI Gen-Core operations module.\nInterfaces with the Groq SDK and manages inference fallback pipelines for Llama models.\n"""\n\nimport os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def call_groq_completions(messages, temperature=0.3, max_tokens=4096):
    try:
        # Try primary model first
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    except Exception as primary_error:
        print(f"Primary model llama-3.3-70b-versatile failed: {str(primary_error)}. Falling back to llama-3.1-8b-instant...")
        try:
            # Automatic fallback to llama-3.1-8b-instant (highly resilient)
            return client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as fallback_error:
            print(f"Fallback model llama-3.1-8b-instant also failed: {str(fallback_error)}")
            raise fallback_error

def post_process_latex(latex_code: str) -> str:
    # 1. Escape unescaped ampersands: (?<!\\)& -> \&
    latex_code = re.sub(r'(?<!\\)&', r'\\&', latex_code)
    
    # 2. Escape unescaped underscores: (?<!\\)_ -> \_
    latex_code = re.sub(r'(?<!\\)_', r'\\_', latex_code)
    
    # 3. Escape unescaped percent signs line-by-line
    lines = latex_code.splitlines()
    for idx, line in enumerate(lines):
        if re.match(r'^\s*%', line):
            continue
        # Replace unescaped % with \%
        lines[idx] = re.sub(r'(?<!\\)%', r'\\%', line)
    latex_code = "\n".join(lines)
    
    # 4. Escape unescaped dollar signs: (?<!\\)\$ -> \$
    latex_code = re.sub(r'(?<!\\)\$', r'\\$', latex_code)
    
    # 5. Fix URL parameters inside \href{URL}{label} and \url{URL}
    # Find all occurrences of \href
    pos = 0
    while True:
        pos = latex_code.find(r"\href", pos)
        if pos == -1:
            break
        
        arg1_start = latex_code.find("{", pos + 5)
        if arg1_start == -1:
            pos += 5
            continue
            
        brace_count = 1
        i = arg1_start + 1
        while i < len(latex_code) and brace_count > 0:
            if latex_code[i] == "{":
                brace_count += 1
            elif latex_code[i] == "}":
                brace_count -= 1
            i += 1
            
        if brace_count == 0:
            arg1_end = i - 1
            url_part = latex_code[arg1_start + 1 : arg1_end]
            fixed_url = url_part.replace(r"\_", "_").replace(r"\&", "&").replace(r"\%", "%").replace(r"\$", "$")
            latex_code = latex_code[:arg1_start + 1] + fixed_url + latex_code[arg1_end:]
            pos = arg1_start + 1 + len(fixed_url)
        else:
            pos += 5
            
    # Also find all occurrences of \url
    pos = 0
    while True:
        pos = latex_code.find(r"\url", pos)
        if pos == -1:
            break
            
        arg1_start = latex_code.find("{", pos + 4)
        if arg1_start == -1:
            pos += 4
            continue
            
        brace_count = 1
        i = arg1_start + 1
        while i < len(latex_code) and brace_count > 0:
            if latex_code[i] == "{":
                brace_count += 1
            elif latex_code[i] == "}":
                brace_count -= 1
            i += 1
            
        if brace_count == 0:
            arg1_end = i - 1
            url_part = latex_code[arg1_start + 1 : arg1_end]
            fixed_url = url_part.replace(r"\_", "_").replace(r"\&", "&").replace(r"\%", "%").replace(r"\$", "$")
            latex_code = latex_code[:arg1_start + 1] + fixed_url + latex_code[arg1_end:]
            pos = arg1_start + 1 + len(fixed_url)
        else:
            pos += 4
            
    return latex_code

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

    completion = call_groq_completions(
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

    completion = call_groq_completions(
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

    completion = call_groq_completions(
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

def generate_tailored_resume(
    resume_text: str,
    job_description: str,
    company_name: str,
    role: str
):
    template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "resources",
        "default_resume.tex"
    )

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            latex_template = f.read()
    except Exception:
        latex_template = "% Default template load failed. Use standard LaTeX resume structure.\n"

    prompt = f"""
You are an expert resume writer, ATS specialist, and LaTeX typesetter.
Task: Generate a tailored resume for "{role}" at "{company_name}" using the provided template, uploaded resume, and job description to maximize ATS score.

CRITICAL RULES:
1. NO SUMMARY: Do NOT include any "Professional Summary", "Summary", or "Objective" section. Completely omit the summary section from the LaTeX code.
2. SECTIONS & CONTENT:
   - Retain all original work experience and education. Rewrite bullet points as high-impact, quantified achievements.
   - ALWAYS include at least three projects. For the projects section, every project heading must be formatted exactly as: `\\resumeProjectHeading{{\\textbf{{Project Name}} - \\emph{{Tech Stack}}}}{{}}`. You MUST use a simple dash symbol ` - ` (space, plain dash, space) as the partition between the Project Name and Tech Stack. DO NOT use `$|$`, `$ - $`, `$—$`, or any other special math mode symbols.
   - Include "Certifications", "Awards", "Languages", or other custom sections only if they exist in the uploaded resume.
   - The final resume must comfortably fill one full page (use 3-4 bullets per job, 2-3 per project). Do not leave excessive empty space.
3. PRESERVE TRUTH & LINKS: Do not invent fake companies, jobs, dates, or degrees. Keep LinkedIn, GitHub, and portfolio links for the header only if they exist in the uploaded resume. DO NOT include any GitHub links, GitHub URLs, or GitHub icons (`\\faGithub` or `\\underline{{GitHub}}`) in the projects section. The second argument of `\\resumeProjectHeading` for every project must be completely empty: `{{}}`.
4. FORMATTING: Preserve the exact LaTeX document class, packages, margins, macros, spacing, and styling of the provided template.
5. ATS TAILORING: Replace weak verbs with strong, active verbs. Naturally integrate key skills from the job description.
6. LATEX SAFETY: You MUST escape all text ampersands (`\\&`), underscores (`\\_`), percent signs (`\\%`), dollar signs (`\\$`), and hash signs (`\\#`) in ordinary text to avoid compilation crashes.

OUTPUT FORMAT (Wrap in respective tags):
<optimized_latex_code>
[Compile-ready LaTeX code starting with \\documentclass and ending with \\end{{document}}]
</optimized_latex_code>

<optimized_resume_text>
[Plain-text version of the final resume]
</optimized_resume_text>

<changes>
[
  {{
    "action": "ADDED / OPTIMIZED",
    "section": "Section name",
    "detail": "Description",
    "reason": "Rationale"
  }}
]
</changes>

LaTeX Template:
{latex_template}

Job Description:
{job_description}

Uploaded Resume:
{resume_text}
"""

    completion = call_groq_completions(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    response_text = completion.choices[0].message.content.strip()

    latex_match = re.search(
        r"<optimized_latex_code>(.*?)</optimized_latex_code>",
        response_text,
        re.DOTALL
    )

    latex_code = latex_match.group(1).strip() if latex_match else ""

    if not latex_code:
        fallback_match = re.search(
            r"\\documentclass.*?\\end\{document\}",
            response_text,
            re.DOTALL
        )
        latex_code = fallback_match.group(0).strip() if fallback_match else ""

    if not latex_code:
        latex_code = "% LaTeX extraction failed.\n" + response_text

    latex_code = post_process_latex(latex_code)

    text_match = re.search(
        r"<optimized_resume_text>(.*?)</optimized_resume_text>",
        response_text,
        re.DOTALL
    )

    optimized_text = text_match.group(1).strip() if text_match else ""

    changes_match = re.search(
        r"<changes>(.*?)</changes>",
        response_text,
        re.DOTALL
    )

    changes = []

    if changes_match:
        try:
            changes_json_str = changes_match.group(1).strip()
            changes_json_str = re.sub(r"```json|```", "", changes_json_str).strip()
            changes = json.loads(changes_json_str)
        except Exception:
            changes = [
                {
                    "action": "OPTIMIZED",
                    "section": "General",
                    "detail": "Resume tailored successfully, but changes JSON could not be parsed.",
                    "reason": "Fallback response added to prevent API failure."
                }
            ]
    else:
        changes = [
            {
                "action": "OPTIMIZED",
                "section": "General",
                "detail": "Resume tailored successfully.",
                "reason": "Aligned resume content with the job description."
            }
        ]

    if not optimized_text:
        optimized_text = latex_to_plain_text(latex_code)

    return {
        "optimized_latex_code": latex_code,
        "optimized_resume_text": optimized_text,
        "changes": changes
    }

def latex_to_plain_text(latex_code: str) -> str:
    text = latex_code

    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\section\{(.*?)\}", r"\n\n\1\n", text)
    text = re.sub(r"\\textbf\{(.*?)\}", r"\1", text)
    text = re.sub(r"\\emph\{(.*?)\}", r"\1", text)
    text = re.sub(r"\\underline\{(.*?)\}", r"\1", text)
    text = re.sub(r"\\href\{.*?\}\{(.*?)\}", r"\1", text)

    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", text)
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()