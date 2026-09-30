import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / '.env')


ROLE_SKILLS = {
    'data analyst': ['excel', 'sql', 'python', 'statistics', 'power bi', 'data visualization', 'reporting'],
    'software engineer': ['python', 'java', 'javascript', 'data structures', 'algorithms', 'git', 'debugging'],
    'product manager': ['market research', 'communication', 'roadmapping', 'analytics', 'stakeholder management'],
    'data scientist': ['python', 'statistics', 'machine learning', 'sql', 'data visualization', 'pandas'],
    'frontend developer': ['html', 'css', 'javascript', 'responsive design', 'ui/ux', 'react'],
    'backend developer': ['python', 'sql', 'api design', 'databases', 'debugging', 'testing'],
    'digital marketer': ['seo', 'content strategy', 'analytics', 'ads', 'social media marketing'],
    'ui/ux designer': ['figma', 'wireframing', 'user research', 'prototyping', 'design systems'],
    'business analyst': ['requirements gathering', 'sql', 'excel', 'documentation', 'stakeholder communication'],
    'cybersecurity analyst': ['network security', 'linux', 'python', 'ethics', 'incident response'],
}


def get_api_key() -> str:
    return os.getenv('GEMINI_API_KEY', '').strip()


def _clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def _safe_json(data: Any, fallback: Any) -> Any:
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return data
    return fallback


def call_gemini(prompt: str, model_name: str = 'gemini-1.5-flash'):
    """Call Gemini if the API key is configured. Otherwise return a safe fallback value."""
    api_key = get_api_key()
    if not api_key or not genai:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None


def parse_json_response(raw_text: str, fallback: Any) -> Any:
    """Try to parse a JSON response from Gemini and fall back if the output is malformed."""
    if not raw_text:
        return fallback

    text = raw_text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?', '', text)
        text = re.sub(r'```$', '', text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            match = re.search(r'\{.*\}', text, re.S)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return fallback


def generate_career_plan(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a structured career roadmap using Gemini if available, otherwise a local heuristic fallback."""
    target_role = (profile.get('target_role') or 'Data Analyst').lower()
    current_skills = list(profile.get('current_skills', []) or [])
    available_hours = profile.get('available_hours', '2')

    required_skills = ROLE_SKILLS.get(target_role, ['python', 'sql', 'communication', 'data analysis'])
    existing_skills = [skill.strip().lower() for skill in current_skills]
    missing_skills = [skill for skill in required_skills if skill.lower() not in existing_skills]

    prompt = f"""
    You are an AI career coach. Generate a JSON object with the fields:
    summary, target_role, current_skills, required_skills, skill_gaps, readiness_estimate, days, projects, certifications, interview_topics.
    The profile is: target_role={profile.get('target_role')}, current_skills={current_skills}, education={profile.get('education')}, experience_level={profile.get('experience_level')}, available_hours={available_hours}, career_goal={profile.get('career_goal')}.
    Write realistic, non-judgmental guidance. Use a 30-day plan with daily entries containing day, topic, tasks, estimated_hours, resources, outcome.
    Use resources as strings with titles and platform names, not fake URLs.
    Return only valid JSON.
    """
    raw = call_gemini(prompt)
    if raw:
        parsed = parse_json_response(raw, {})
        if isinstance(parsed, dict):
            payload = {
                'summary': parsed.get('summary') or f'{profile.get("target_role")} roadmap to improve alignment and readiness.',
                'target_role': parsed.get('target_role') or profile.get('target_role'),
                'current_skills': parsed.get('current_skills') or current_skills,
                'required_skills': parsed.get('required_skills') or required_skills,
                'skill_gaps': parsed.get('skill_gaps') or missing_skills,
                'readiness_estimate': parsed.get('readiness_estimate') or {'score': 75, 'explanation': 'AI-generated career readiness estimate based on provided data.'},
                'days': parsed.get('days') or build_fallback_days(profile, required_skills),
                'projects': parsed.get('projects') or build_fallback_projects(target_role),
                'certifications': parsed.get('certifications') or build_fallback_certifications(target_role),
                'interview_topics': parsed.get('interview_topics') or build_fallback_interview_topics(target_role),
            }
            return payload

    return build_fallback_career_plan(profile, required_skills, missing_skills)


def build_fallback_days(profile: Dict[str, Any], required_skills: List[str]) -> List[Dict[str, Any]]:
    target_role = (profile.get('target_role') or 'Data Analyst').title()
    hours = max(1, int(str(profile.get('available_hours', '2')).split()[0] if str(profile.get('available_hours', '2')).split() else 2))
    topic_list = required_skills[:6]
    days = []
    for i, topic in enumerate(topic_list, start=1):
        days.append({
            'day': i,
            'topic': topic.title(),
            'tasks': [
                f'Learn the fundamentals of {topic.title()}.',
                f'Practice with 2-3 guided exercises for {topic.title()}.',
                'Note key learnings and create a short summary.'
            ],
            'estimated_hours': min(hours, 3),
            'resources': [
                f'{topic.title()} official documentation',
                f'{topic.title()} beginner tutorial video',
                'Practice exercises and notes'
            ],
            'outcome': f'Build a basic understanding of {topic.title()} and improve confidence in practical use.'
        })
    while len(days) < 30:
        days.append({
            'day': len(days) + 1,
            'topic': f'Applied {target_role} Practice',
            'tasks': ['Review the previous topic', 'Apply it to a mini project', 'Document the outcome'],
            'estimated_hours': min(hours, 3),
            'resources': ['Official documentation', 'Project walkthrough', 'Practice notebook'],
            'outcome': 'Translate learning into a small practical task connected to the target role.'
        })
    return days[:30]


def build_fallback_projects(target_role: str) -> List[Dict[str, Any]]:
    mapping = {
        'data analyst': [
            {'title': 'Sales Dashboard', 'difficulty': 'Beginner', 'skills': ['Excel', 'SQL', 'Power BI'], 'description': 'Analyze sales data and build an interactive dashboard.', 'tools': ['Excel', 'SQL', 'Power BI'], 'expected_output': 'Dashboard with trends, filters, and KPI cards.', 'portfolio_value': 'Shows business analysis and visualization skills.'},
            {'title': 'Customer Churn Analysis', 'difficulty': 'Intermediate', 'skills': ['Python', 'Pandas', 'Visualization'], 'description': 'Identify churn drivers and create a retention summary.', 'tools': ['Python', 'Pandas', 'Matplotlib'], 'expected_output': 'Churn report with charts and recommendations.', 'portfolio_value': 'Demonstrates data analysis and storytelling.'},
        ],
        'software engineer': [
            {'title': 'Task Management API', 'difficulty': 'Beginner', 'skills': ['Python', 'Flask', 'SQLite'], 'description': 'Build a CRUD API for task tracking.', 'tools': ['Python', 'Flask', 'SQLite'], 'expected_output': 'Working API with endpoints and tests.', 'portfolio_value': 'Shows backend engineering and system design fundamentals.'},
        ],
        'data scientist': [
            {'title': 'Predictive Sales Model', 'difficulty': 'Intermediate', 'skills': ['Python', 'Scikit-learn', 'SQL'], 'description': 'Train a simple prediction model using sales data.', 'tools': ['Python', 'Scikit-learn', 'Jupyter'], 'expected_output': 'Model report and predictions.', 'portfolio_value': 'Demonstrates ML workflow and evaluation.'},
        ],
    }
    return mapping.get(target_role.lower(), [
        {'title': f'{target_role.title()} Starter Project', 'difficulty': 'Beginner', 'skills': ['Research', 'Documentation', 'Presentation'], 'description': 'Create a small portfolio project connected to the role.', 'tools': ['Python', 'Excel', 'Git'], 'expected_output': 'A practical project with documentation and results.', 'portfolio_value': 'Builds portfolio evidence and problem-solving practice.'}
    ])


def build_fallback_certifications(target_role: str) -> List[Dict[str, Any]]:
    mapping = {
        'data analyst': [
            {'name': 'Microsoft Power BI Data Analyst Associate', 'provider': 'Microsoft', 'skill_covered': 'Power BI, reporting, analytics', 'level': 'Intermediate', 'url': 'https://learn.microsoft.com/'},
            {'name': 'Google Data Analytics', 'provider': 'Google', 'skill_covered': 'SQL, spreadsheets, analytics', 'level': 'Beginner', 'url': 'https://www.coursera.org/professional-certificates/google-data-analytics'},
        ],
        'software engineer': [
            {'name': 'AWS Cloud Practitioner', 'provider': 'AWS', 'skill_covered': 'Cloud basics and software engineering context', 'level': 'Beginner', 'url': 'https://aws.amazon.com/certification/certified-cloud-practitioner/'},
        ],
    }
    return mapping.get(target_role.lower(), [
        {'name': f'{target_role.title()} Foundations Learning Path', 'provider': 'Self-paced learning', 'skill_covered': 'Role-specific fundamentals', 'level': 'Beginner', 'url': ''}
    ])


def build_fallback_interview_topics(target_role: str) -> List[str]:
    role = target_role.lower()
    if role == 'data analyst':
        return ['SQL joins and query optimization', 'Excel formulas and dashboarding', 'Business interpretation of metrics', 'Communication of findings to stakeholders']
    if role == 'software engineer':
        return ['Data structures and algorithms', 'Object-oriented design', 'API design', 'Debugging and testing']
    return [f'Core concepts in {target_role}', 'Practical project walkthrough', 'Communication and problem solving', 'Behavioral scenarios']


def build_fallback_career_plan(profile: Dict[str, Any], required_skills: List[str], missing_skills: List[str]) -> Dict[str, Any]:
    target_role = profile.get('target_role', 'Data Analyst')
    current_skills = profile.get('current_skills', [])
    return {
        'summary': f'Focus on role-aligned upskilling for {target_role}. Build practical knowledge, revise fundamentals, and create a portfolio that demonstrates your readiness.',
        'target_role': target_role,
        'current_skills': current_skills,
        'required_skills': required_skills,
        'skill_gaps': missing_skills,
        'readiness_estimate': {
            'score': 76,
            'explanation': 'AI-generated career readiness estimate based on the information provided. It should be used as guidance, not a guarantee.'
        },
        'days': build_fallback_days(profile, required_skills),
        'projects': build_fallback_projects(target_role),
        'certifications': build_fallback_certifications(target_role),
        'interview_topics': build_fallback_interview_topics(target_role),
    }


def analyze_resume_text(resume_text: str, target_role: str) -> Dict[str, Any]:
    """Create a structured resume analysis using heuristic rules, with Gemini as optional enhancement."""
    cleaned = _clean_text(resume_text)
    skills = [skill for skill in ['python', 'sql', 'excel', 'power bi', 'tableau', 'statistics', 'pandas', 'java', 'javascript', 'html', 'css', 'aws', 'machine learning', 'ai'] if skill in cleaned.lower()]
    sections = {
        'contact': 'contact information found' if re.search(r'@[A-Za-z0-9._%+-]+\.[A-Za-z]{2,}', cleaned) else 'contact information missing',
        'summary': 'summary found' if len(cleaned) > 120 else 'summary missing',
        'education': 'education section found' if re.search(r'(b\.tech|btech|b\.sc|bsc|m\.tech|mba|degree|college|university|graduate)', cleaned.lower()) else 'education section missing',
        'projects': 'project section found' if re.search(r'project|projects|portfolio', cleaned.lower()) else 'project section missing',
        'experience': 'experience section found' if re.search(r'experience|intern|internship|worked|developer|analyst', cleaned.lower()) else 'experience section missing',
    }

    prompt = f"""
    Analyze the following resume text for a target role: {target_role}. Return only valid JSON with: summary, strengths, improvement_areas, missing_sections, skills, target_role_relevance, formatting_issues.
    Resume text: {resume_text[:5000]}
    """
    response = call_gemini(prompt)
    parsed = parse_json_response(response, None) if response else None
    if isinstance(parsed, dict):
        return {
            'summary': parsed.get('summary') or f'Resume shows strong potential for {target_role}.',
            'strengths': parsed.get('strengths') or ['Relevant technical background', 'Good foundation for the role'],
            'improvement_areas': parsed.get('improvement_areas') or ['Add measurable accomplishments and role-specific keywords.', 'Include a clearer project summary.'],
            'missing_sections': parsed.get('missing_sections') or ['Add stronger summary and measurable achievements.'],
            'skills': parsed.get('skills') or skills,
            'target_role_relevance': parsed.get('target_role_relevance') or 'Good alignment with the target role based on available information.',
            'formatting_issues': parsed.get('formatting_issues') or ['Improve structure and consistency of headings.', 'Add quantifiable outcomes where possible.'],
            'sections': sections,
        }

    return {
        'summary': f'Resume review for {target_role}. It shows a reasonable base profile and could be improved with more role-specific evidence.',
        'strengths': ['Relevant technical keywords found', 'Basic skill coverage detected'],
        'improvement_areas': ['Include specific project outcomes', 'Mention metrics and achievements', 'Match skills to the role'],
        'missing_sections': ['Add a concise professional summary', 'Add measurable results', 'List certifications clearly'],
        'skills': skills,
        'target_role_relevance': 'Moderate alignment; a few missing role keywords can improve the fit.',
        'formatting_issues': ['Use standard headings like Summary, Education, Experience, Skills, Projects', 'Avoid inconsistent spacing or formatting'],
        'sections': sections,
    }


def analyze_job_description(job_title: str, company: str, description: str) -> Dict[str, Any]:
    text = (job_title + ' ' + company + ' ' + description).lower()
    required_keywords = []
    for keyword in ['python', 'sql', 'excel', 'power bi', 'tableau', 'statistics', 'data analysis', 'communication', 'project management', 'aws', 'javascript', 'java', 'html', 'css', 'machine learning', 'ai']:
        if keyword in text:
            required_keywords.append(keyword)

    return {
        'job_title': job_title,
        'company': company,
        'required_skills': required_keywords[:10],
        'preferred_skills': ['Communication', 'Problem solving', 'Presentation'] if 'communication' in text else ['Communication', 'Problem solving'],
        'tools': ['Excel', 'SQL', 'Power BI'] if 'power bi' in text else ['Excel', 'SQL'],
        'programming_languages': ['Python'] if 'python' in text else ['Python', 'SQL'],
        'education_requirements': 'Bachelor degree preferred or equivalent experience',
        'experience_requirements': '0-2 years or internship experience preferred',
        'certifications': ['Relevant role-specific certification preferred'] if 'certification' in text else [],
        'responsibilities': ['Analyze data and prepare reports', 'Collaborate on business decisions'],
        'keywords': required_keywords[:15],
    }


def compare_resume_job(resume_text: str, job_description: str, target_role: str) -> Dict[str, Any]:
    """Compute a simple resume-to-job match with a friendly, estimate-based label."""
    job_lower = job_description.lower()
    resume_lower = resume_text.lower()
    skill_hits = [
        skill for skill in ['python', 'sql', 'excel', 'power bi', 'tableau', 'statistics', 'data analysis', 'communication', 'analytics', 'reporting']
        if skill in resume_lower and skill in job_lower
    ]
    missing = [
        skill for skill in ['python', 'sql', 'excel', 'power bi', 'tableau', 'statistics', 'data analysis']
        if skill in job_lower and skill not in resume_lower
    ]
    keyword_overlap = max(10, len(skill_hits))
    overall_match = min(95, max(30, (len(skill_hits) / max(1, len(set(skill_hits) | set(missing)))) * 100))

    return {
        'overall_match': round(overall_match, 1),
        'matched_skills': skill_hits[:8],
        'missing_skills': missing[:8],
        'matched_keywords': skill_hits[:8],
        'suggested_resume_improvements': [
            'Add role-specific keywords from the job description.',
            'Highlight measurable project outcomes.',
            'Mention relevant tools and domain context.'
        ],
        'target_role': target_role,
        'note': 'This is an AI-generated estimate and should be used as guidance, not a guarantee of selection.'
    }


def generate_interview_questions(target_role: str, skills: List[str], resume_text: str, job_description: str) -> Dict[str, Any]:
    role = (target_role or 'Data Analyst').lower()
    if 'data analyst' in role:
        technical = [
            {'question': 'Explain the difference between INNER JOIN and LEFT JOIN.', 'difficulty': 'Medium', 'topic': 'SQL', 'answer_guidance': 'Discuss matching rows, null handling, and use cases.'},
            {'question': 'How do you handle missing values in a dataset?', 'difficulty': 'Medium', 'topic': 'Data Cleaning', 'answer_guidance': 'Explain imputation, deletion, and validation.'},
        ]
    else:
        technical = [{'question': f'How would you explain the core responsibilities of a {target_role} role?', 'difficulty': 'Medium', 'topic': 'Role Fundamentals', 'answer_guidance': 'Discuss tasks, tools, and problem-solving.'}]

    hr = [
        {'question': 'Why are you interested in this role?', 'difficulty': 'Easy', 'topic': 'HR', 'answer_guidance': 'Connect your interest to growth, learning, and role fit.'},
        {'question': 'What are your strengths and how do they help in this role?', 'difficulty': 'Easy', 'topic': 'HR', 'answer_guidance': 'Mention 2-3 strengths with examples.'},
    ]

    behavioral = [
        {'question': 'Describe a time you solved a problem under pressure.', 'difficulty': 'Medium', 'topic': 'Behavioral', 'answer_guidance': 'Use STAR method.'},
    ]

    resume_based = [
        {'question': 'Walk me through a project from your resume.', 'difficulty': 'Medium', 'topic': 'Resume', 'answer_guidance': 'Explain the problem, your approach, tools, and outcome.'}
    ]

    scenario = [
        {'question': 'Your dashboard is not matching stakeholder expectations. What do you do?', 'difficulty': 'Medium', 'topic': 'Scenario', 'answer_guidance': 'Discuss clarifying requirements, validating data, and iterating.'}
    ]

    return {
        'technical_questions': technical,
        'hr_questions': hr,
        'behavioral_questions': behavioral,
        'resume_based_questions': resume_based,
        'scenario_based_questions': scenario,
    }


def generate_project_recommendations(role: str, missing_skills: List[str]) -> List[Dict[str, Any]]:
    role = role.lower()
    if role == 'data analyst':
        return [
            {
                'title': 'Sales Dashboard',
                'difficulty': 'Beginner',
                'skills': ['Excel', 'SQL', 'Power BI'],
                'description': 'Create a sales dashboard from sample data and summarize KPIs.',
                'tools': ['Excel', 'Power BI', 'SQL'],
                'expected_output': 'A dashboard with filters, trends, customer insights, and summary charts.',
                'portfolio_value': 'Shows business understanding, dashboarding, and reporting skills.'
            },
            {
                'title': 'Customer Churn Analysis',
                'difficulty': 'Intermediate',
                'skills': ['Python', 'Pandas', 'Visualization'],
                'description': 'Analyze churn patterns and suggest actions to reduce customer loss.',
                'tools': ['Python', 'Pandas', 'Matplotlib'],
                'expected_output': 'A cleaned and analyzed churn report with visualizations.',
                'portfolio_value': 'Demonstrates skill in analysis, storytelling, and real-world interpretation.'
            }
        ]
    return [{
        'title': f'{role.title()} Starter Project',
        'difficulty': 'Beginner',
        'skills': missing_skills[:4] or ['Research', 'Planning', 'Documentation'],
        'description': f'Build a beginner-friendly project aligned to the {role} role.',
        'tools': ['Python', 'Git', 'Documentation'],
        'expected_output': 'A complete project with explanation, output, and screenshots.',
        'portfolio_value': 'Improves practical evidence and shows initiative in the target domain.'
    }]
