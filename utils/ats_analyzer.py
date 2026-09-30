import re
from typing import Dict, List


def normalize_words(text: str) -> List[str]:
    """Return a cleaned list of lowercase words from a text block."""
    if not text:
        return []
    return re.findall(r'[A-Za-z][A-Za-z0-9+#. /-]*', text.lower())


def extract_keywords(text: str) -> List[str]:
    """Extract candidate keywords (skills, tools, frameworks, and common nouns)."""
    words = normalize_words(text)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'for', 'with', 'to', 'of', 'in', 'on', 'is', 'are', 'be',
        'as', 'at', 'by', 'from', 'this', 'that', 'these', 'those', 'your', 'our', 'their', 'you',
        'we', 'they', 'project', 'role', 'experience', 'resume', 'job', 'career', 'skills', 'work',
        'worked', 'using', 'based', 'into', 'about', 'over', 'under', 'than'
    }
    keywords = []
    for word in words:
        if len(word) > 2 and word not in stop_words:
            keywords.append(word)
    return keywords


def safe_score(percentage: float) -> int:
    """Clamp a calculation to the 0-100 range."""
    return max(0, min(100, int(round(percentage))))


def analyze_ats_compatibility(resume_text: str, job_description: str, target_role: str) -> Dict[str, object]:
    """Compute a simple ATS compatibility estimate based on keyword overlap and document clarity."""
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_description))

    overlaps = sorted(resume_keywords.intersection(job_keywords))
    keyword_match = 0 if not job_keywords else safe_score((len(overlaps) / max(len(job_keywords), 1)) * 100)

    skills_to_match = {
        'python', 'sql', 'excel', 'power bi', 'tableau', 'statistics', 'pandas',
        'data analysis', 'reporting', 'analytics', 'machine learning', 'presentation',
        'communication', 'problem solving', 'java', 'javascript', 'html', 'css',
        'aws', 'cloud', 'ai', 'ml', 'business intelligence'
    }

    resume_skill_text = resume_text.lower()
    matched_skills = [skill for skill in sorted(skills_to_match) if skill in resume_skill_text]
    desired_skills = [skill for skill in sorted(skills_to_match) if skill in job_description.lower()]
    skills_match = 0 if not desired_skills else safe_score((len(matched_skills) / max(len(desired_skills), 1)) * 100)

    experience_relevance = safe_score(80 if 'experience' in job_description.lower() else 88)
    resume_structure = 90 if resume_text and len(resume_text) > 200 else 70
    readability = 85 if len(resume_text) > 200 else 72

    suggestions = []
    if keyword_match < 85:
        suggestions.append('Add missing technical keywords from the target role and job description.')
    if skills_match < 80:
        suggestions.append('Match your resume skills more closely to the job requirements.')
    if 'summary' not in resume_text.lower() and 'professional summary' not in resume_text.lower():
        suggestions.append('Add a clear professional summary near the top of the resume.')
    if 'experience' not in resume_text.lower() and 'projects' not in resume_text.lower():
        suggestions.append('Include measurable project and work experience examples.')
    suggestions = suggestions[:6]

    return {
        'target_role': target_role,
        'ats_compatibility_estimate': safe_score((keyword_match * 0.35) + (skills_match * 0.30) + (experience_relevance * 0.15) + (resume_structure * 0.10) + (readability * 0.10)),
        'breakdown': {
            'keyword_match': keyword_match,
            'skills_match': skills_match,
            'experience_relevance': experience_relevance,
            'resume_structure': resume_structure,
            'readability': readability,
        },
        'matched_keywords': overlaps[:12],
        'missing_keywords': sorted(set(job_keywords) - set(resume_keywords))[:12],
        'suggestions': suggestions,
    }
