import os
import re
from collections import Counter
import openai
from pypdf import PdfReader

STOP_WORDS = {
    "and", "or", "the", "a", "an", "to", "for", "with", "in", "on", "of", "is", "are", "by", "as",
    "that", "this", "from", "at", "be", "have", "has", "using", "use", "will", "can", "will",
}

COMMON_SKILLS = {
    "python", "java", "c++", "c#", "sql", "excel", "javascript", "react", "angular", "node.js", "django",
    "flask", "git", "docker", "kubernetes", "aws", "azure", "gcp", "machine learning", "data analysis",
    "nlp", "cloud", "leadership", "project management", "communication", "linux", "html", "css", "rest api",
    "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "javascript", "typescript", "salesforce",
    "accounting", "finance", "marketing", "seo", "business analysis", "sql server", "oracle", "tableau",
    "power bi", "bi", "agile", "scrum", "testing", "qa", "automation", "devops", "security",
    "mobile", "ios", "android", "unity", "kotlin", "swift", "react native", "ux", "ui", "design",
}

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\+\#\. ]", " ", text)
    return text.strip()


def extract_text_from_pdf(pdf_file) -> str:
    try:
        reader = PdfReader(pdf_file)
        raw_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            raw_text.append(text)
        return "\n\n".join(raw_text).strip()
    except Exception as exc:
        return f"Error extracting text from PDF: {exc}"


def tokenize(text: str) -> list[str]:
    clean = normalize_text(text)
    tokens = [token for token in re.split(r"\W+", clean) if token and token not in STOP_WORDS]
    return tokens


def extract_skills(text: str) -> set[str]:
    text_norm = normalize_text(text)
    found = set()
    for skill in COMMON_SKILLS:
        if skill in text_norm:
            found.add(skill.title() if skill.islower() else skill)

    # detect multi-word skills from raw text patterns
    phrases = ["machine learning", "project management", "data analysis", "power bi", "rest api", "react native"]
    for phrase in phrases:
        if phrase in text_norm:
            found.add(phrase.title())

    return found


def score_text_similarity(resume_text: str, job_text: str) -> int:
    resume_tokens = set(tokenize(resume_text))
    job_tokens = set(tokenize(job_text))
    if not resume_tokens or not job_tokens:
        return 0

    shared_tokens = resume_tokens.intersection(job_tokens)
    overlap = len(shared_tokens) / max(len(job_tokens), 1)
    return min(100, round(overlap * 100))


def compute_match_score(resume_text: str, job_text: str, resume_skills: set[str], job_skills: set[str]) -> int:
    skill_score = 0
    if job_skills:
        skill_matches = resume_skills.intersection(job_skills)
        skill_score = round(len(skill_matches) / len(job_skills) * 100)

    text_score = score_text_similarity(resume_text, job_text)
    combined = round((skill_score * 0.6) + (text_score * 0.4))
    return min(100, combined)


def get_missing_skills(resume_skills: set[str], job_skills: set[str]) -> list[str]:
    return sorted(job_skills.difference(resume_skills))


def generate_actionable_suggestions(resume_skills: set[str], job_skills: set[str], missing_skills: list[str]) -> list[str]:
    suggestions = []
    if missing_skills:
        top_missing = ", ".join(missing_skills[:3])
        suggestions.append(
            f"Add the missing keywords exactly as written in the job description, such as {top_missing}. Place them in a dedicated skills section and in 1–2 experience bullets that describe how you used each skill to achieve a real outcome."
        )
    else:
        top_skills = ", ".join(list(job_skills)[:3]) or "the main job skills"
        suggestions.append(
            f"Your resume already contains the key role skills. Make them more compelling by repeating the top job keywords ({top_skills}) in your summary, the first bullet of each relevant job, and a separate skills section."
        )

    suggestions.append(
        "Replace generic duties with specific results statements that include numbers, timelines, and context, for example: 'Delivered a 25% conversion lift in 6 months using React, AWS, and A/B testing.'"
    )
    suggestions.append(
        "Use section headings and keywords that match the job posting, such as 'Professional Experience', 'Technical Skills', and 'Project Highlights', so both ATS and hiring managers recognize the fit immediately."
    )
    return suggestions[:3]


def call_openai_for_suggestions(resume_text: str, job_text: str) -> list[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    openai.api_key = api_key
    prompt = (
        "You are an ATS assistant. Review the resume and job description below, then provide 3 specific, actionable suggestions that if implemented will improve the candidate's chance of landing the desired role. "
        "Focus on exact keyword matching, measurable accomplishments, formatting for ATS, and missing target skills.\n\n"
        f"Resume text:\n{resume_text[:3000]}\n\n"
        f"Job description:\n{job_text[:3000]}\n\n"
        "Respond with three short bullet points, each starting with a clear action that will help the candidate land the job."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        content = response.choices[0].message.content.strip()
        suggestions = [line.strip(" -\n") for line in content.splitlines() if line.strip()]
        return suggestions[:3]
    except Exception:
        return []


def analyze_resume(resume_text: str, job_description: str) -> dict[str, any]:
    if not resume_text or not job_description:
        return {
            "match_score": 0,
            "resume_skills": set(),
            "job_skills": set(),
            "missing_skills": [],
            "ats_suggestions": [],
        }

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    match_score = compute_match_score(resume_text, job_description, resume_skills, job_skills)
    missing_skills = get_missing_skills(resume_skills, job_skills)
    ats_suggestions = call_openai_for_suggestions(resume_text, job_description)

    if not ats_suggestions:
        ats_suggestions = generate_actionable_suggestions(resume_skills, job_skills, missing_skills)

    return {
        "match_score": match_score,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "missing_skills": missing_skills,
        "ats_suggestions": ats_suggestions,
    }
