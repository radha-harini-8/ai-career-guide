import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from utils.ats_analyzer import analyze_ats_compatibility
from utils.gemini import (
    analyze_job_description,
    analyze_resume_text,
    compare_resume_job,
    generate_career_plan,
    generate_interview_questions,
    generate_project_recommendations,
)
from utils.json_storage import add_record, get_all_records, get_record, load_json, save_json
from utils.resume_parser import extract_resume_text

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def success_response(data=None):
    return jsonify({"success": True, "data": data or {}})


def error_response(message):
    return jsonify({"success": False, "error": message}), 400


def normalize_skills(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def find_latest_record(records, user_id):
    matching = [record for record in records if record.get('user_id') == user_id]
    if not matching:
        return None
    return sorted(matching, key=lambda item: item.get('updated_at', item.get('created_at', '')))[-1]


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/career-guide')
def career_guide_page():
    return render_template('career-guide.html')


@app.route('/resume-analyzer')
def resume_analyzer_page():
    return render_template('resume-analyzer.html')


@app.route('/job-analyzer')
def job_analyzer_page():
    return render_template('job-analyzer.html')


@app.route('/interview-prep')
def interview_prep_page():
    return render_template('interview-prep.html')


@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/report')
def report_page():
    return render_template('report.html')


@app.route('/api/resources')
def get_resources():
    resources = [
        {"title": "SQL Tutorial", "platform": "W3Schools", "description": "Learn SQL basics and query writing.", "url": "https://www.w3schools.com/sql/"},
        {"title": "Excel Training", "platform": "Microsoft Learn", "description": "Learn Excel formulas and data analysis fundamentals.", "url": "https://learn.microsoft.com/en-us/training/paths/excel/"},
        {"title": "Python for Data Analysis", "platform": "Coursera", "description": "Learn Python, Pandas, and data analysis workflows.", "url": "https://www.coursera.org/learn/data-analysis-with-python"},
        {"title": "Power BI Basics", "platform": "Microsoft Learn", "description": "Learn Power BI dashboard building and data modeling.", "url": "https://learn.microsoft.com/en-us/training/paths/power-bi/"},
        {"title": "Statistics Essentials", "platform": "Khan Academy", "description": "Build statistics foundations for analytics and data roles.", "url": "https://www.khanacademy.org/math/statistics-probability"},
    ]
    return success_response({"resources": resources})


@app.route('/api/career-plan', methods=['POST'])
def create_career_plan():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Please provide the required form details.')

    required_fields = ['name', 'target_role', 'current_skills', 'education', 'experience_level', 'available_hours', 'career_goal']
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return error_response('Please fill in all required fields before generating a career plan.')

    user_id = payload.get('user_id') or f'user_{uuid.uuid4().hex[:8]}'
    normalized_skills = normalize_skills(payload.get('current_skills'))
    user = {
        'id': user_id,
        'name': payload.get('name', '').strip(),
        'target_role': payload.get('target_role', '').strip(),
        'skills': normalized_skills,
        'education': payload.get('education', '').strip(),
        'experience_level': payload.get('experience_level', '').strip(),
        'available_hours': payload.get('available_hours', '').strip(),
        'career_goal': payload.get('career_goal', '').strip(),
        'created_at': utc_now_iso(),
        'updated_at': utc_now_iso(),
    }

    existing_users = load_json(BASE_DIR / 'data' / 'users.json', [])
    if not any(item.get('id') == user_id for item in existing_users):
        add_record(BASE_DIR / 'data' / 'users.json', user)
    else:
        users = existing_users
        for item in users:
            if item.get('id') == user_id:
                item.update(user)
                break
        save_json(BASE_DIR / 'data' / 'users.json', users)

    plan = generate_career_plan({
        'name': user['name'],
        'target_role': user['target_role'],
        'current_skills': normalized_skills,
        'education': user['education'],
        'experience_level': user['experience_level'],
        'available_hours': user['available_hours'],
        'career_goal': user['career_goal'],
    })

    record = {
        'id': f'plan_{uuid.uuid4().hex[:8]}',
        'user_id': user_id,
        'created_at': utc_now_iso(),
        'updated_at': utc_now_iso(),
        'plan': plan,
    }
    add_record(BASE_DIR / 'data' / 'career_plans.json', record)
    return success_response({'user_id': user_id, 'plan': plan})


@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    file = request.files.get('resume')
    target_role = request.form.get('target_role', 'Data Analyst')

    if not file or file.filename == '':
        return error_response('Please upload a resume file.')

    if file and file.filename:
        try:
            original_name = file.filename
            safe_name = original_name
            file_bytes = file.read()
            extracted = extract_resume_text(file_bytes, safe_name)
            text = extracted['text']

            result = analyze_resume_text(text, target_role)
            record = {
                'id': f'resume_{uuid.uuid4().hex[:8]}',
                'user_id': request.form.get('user_id') or f'user_{uuid.uuid4().hex[:8]}',
                'target_role': target_role,
                'filename': extracted['filename'],
                'career_readiness': {'score': 75, 'label': 'AI-generated career readiness estimate'},
                'analysis': result,
                'created_at': utc_now_iso(),
                'updated_at': utc_now_iso(),
            }
            add_record(BASE_DIR / 'data' / 'resume_analysis.json', record)
            return success_response({'analysis': result, 'filename': extracted['filename']})
        except ValueError as exc:
            return error_response(str(exc))
        except Exception as exc:
            print(f'Resume analysis failed: {exc}')
            return error_response('Something went wrong while analyzing your resume. Please try again.')

    return error_response('No resume file was sent.')


@app.route('/api/analyze-job', methods=['POST'])
def analyze_job():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Please provide a job title and description.')

    job_title = (payload.get('job_title') or '').strip()
    company = (payload.get('company') or '').strip()
    description = (payload.get('job_description') or payload.get('description') or '').strip()
    if not job_title or not description:
        return error_response('Job title and description are required.')

    output = analyze_job_description(job_title, company, description)
    record = {
        'id': f'job_{uuid.uuid4().hex[:8]}',
        'user_id': payload.get('user_id') or f'user_{uuid.uuid4().hex[:8]}',
        'job_title': job_title,
        'company': company,
        'description': description,
        'analysis': output,
        'created_at': utc_now_iso(),
        'updated_at': utc_now_iso(),
    }
    add_record(BASE_DIR / 'data' / 'job_analysis.json', record)
    return success_response({'analysis': output})


@app.route('/api/match-resume', methods=['POST'])
def match_resume():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Resume and job description are required.')

    resume_text = payload.get('resume_text') or ''
    job_description = payload.get('job_description') or ''
    target_role = payload.get('target_role') or 'Data Analyst'

    if not resume_text or not job_description:
        file = request.files.get('resume') if request.files else None
        if file and file.filename:
            try:
                file_bytes = file.read()
                extracted = extract_resume_text(file_bytes, file.filename)
                resume_text = extracted['text']
            except Exception:
                return error_response('Unable to read the uploaded resume.')
        else:
            return error_response('Please provide resume text or upload a resume file and a job description.')

    match_result = compare_resume_job(resume_text, job_description, target_role)
    ats_result = analyze_ats_compatibility(resume_text, job_description, target_role)
    response = {'match': match_result, 'ats': ats_result}
    return success_response(response)


@app.route('/api/interview', methods=['POST'])
def interview_api():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Please provide the required interview details.')

    target_role = payload.get('target_role', 'Data Analyst')
    skills = normalize_skills(payload.get('skills', ''))
    resume_text = payload.get('resume_text') or ''
    job_description = payload.get('job_description') or ''

    questions = generate_interview_questions(target_role, skills, resume_text, job_description)
    interview_record = {
        'id': f'interview_{uuid.uuid4().hex[:8]}',
        'user_id': payload.get('user_id') or f'user_{uuid.uuid4().hex[:8]}',
        'target_role': target_role,
        'questions': questions,
        'created_at': utc_now_iso(),
        'updated_at': utc_now_iso(),
    }
    add_record(BASE_DIR / 'data' / 'interview_sessions.json', interview_record)
    return success_response({'questions': questions})


@app.route('/api/projects', methods=['POST'])
def project_api():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Please provide a target role and skill gap information.')

    role = payload.get('target_role', 'Data Analyst')
    missing_skills = normalize_skills(payload.get('missing_skills', ''))
    projects = generate_project_recommendations(role, missing_skills)
    return success_response({'projects': projects})


@app.route('/api/certifications', methods=['POST'])
def certifications_api():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Please provide a target role.')

    role = payload.get('target_role', 'Data Analyst')
    missing_skills = normalize_skills(payload.get('missing_skills', ''))
    certs = []
    role_lower = role.lower()
    if 'data analyst' in role_lower:
        certs = [
            {'name': 'Microsoft Power BI Data Analyst Associate', 'provider': 'Microsoft', 'skill_covered': 'Power BI, reporting, analytics', 'level': 'Intermediate', 'url': 'https://learn.microsoft.com/'},
            {'name': 'Google Data Analytics', 'provider': 'Google', 'skill_covered': 'SQL, spreadsheets, and analytics', 'level': 'Beginner', 'url': 'https://www.coursera.org/professional-certificates/google-data-analytics'},
        ]
    elif 'software' in role_lower or 'developer' in role_lower:
        certs = [
            {'name': 'AWS Cloud Practitioner', 'provider': 'AWS', 'skill_covered': 'Cloud concepts and software engineering context', 'level': 'Beginner', 'url': 'https://aws.amazon.com/certification/certified-cloud-practitioner/'},
        ]
    else:
        certs = [{'name': f'{role} Fundamentals', 'provider': 'Self-paced learning', 'skill_covered': ' '.join(missing_skills[:3]) or 'Role fundamentals', 'level': 'Beginner', 'url': ''}]

    return success_response({'certifications': certs})


@app.route('/api/progress', methods=['POST'])
def update_progress():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return error_response('Progress payload is missing.')

    user_id = payload.get('user_id')
    if not user_id:
        return error_response('User ID is required to save progress.')

    completed_days = payload.get('completed_days', [])
    progress = payload.get('progress', 0)
    record = {
        'id': f'progress_{uuid.uuid4().hex[:8]}',
        'user_id': user_id,
        'completed_days': completed_days,
        'progress': progress,
        'created_at': utc_now_iso(),
        'updated_at': utc_now_iso(),
    }
    add_record(BASE_DIR / 'data' / 'progress.json', record)
    return success_response({'progress': record})


@app.route('/api/dashboard/<user_id>')
def dashboard_data(user_id):
    users = get_all_records(BASE_DIR / 'data' / 'users.json')
    user = next((item for item in users if item.get('id') == user_id), None)
    plans = get_all_records(BASE_DIR / 'data' / 'career_plans.json')
    plan = find_latest_record(plans, user_id)
    progress_entries = get_all_records(BASE_DIR / 'data' / 'progress.json')
    progress_record = find_latest_record(progress_entries, user_id)
    resume_records = get_all_records(BASE_DIR / 'data' / 'resume_analysis.json')
    resume_record = find_latest_record(resume_records, user_id)

    target_role = user.get('target_role') if user else (plan.get('plan', {}).get('target_role') if plan else 'Data Analyst')
    readiness = plan.get('plan', {}).get('readiness_estimate', {}).get('score', 76) if plan else 76
    ats_estimate = 82
    if resume_record and resume_record.get('analysis'):
        ats_estimate = resume_record.get('analysis', {}).get('ats_estimate', ats_estimate)
    learning_progress = progress_record.get('progress', 0) if progress_record else 0
    skill_gap_count = len(plan.get('plan', {}).get('skill_gaps', [])) if plan else 3

    dashboard = {
        'user': user or {'name': 'Student', 'target_role': target_role},
        'target_role': target_role,
        'career_readiness': readiness,
        'resume_ats_estimate': ats_estimate,
        'skill_match': '8/11',
        'learning_progress': learning_progress,
        'skill_gap': skill_gap_count,
        'plan': plan.get('plan') if plan else {},
    }
    return success_response({'dashboard': dashboard})


@app.route('/api/report/<user_id>')
def report_data(user_id):
    user = get_record(BASE_DIR / 'data' / 'users.json', user_id)
    plans = get_all_records(BASE_DIR / 'data' / 'career_plans.json')
    plan_record = find_latest_record(plans, user_id)
    resume_records = get_all_records(BASE_DIR / 'data' / 'resume_analysis.json')
    resume_record = find_latest_record(resume_records, user_id)
    progress_entries = get_all_records(BASE_DIR / 'data' / 'progress.json')
    progress_record = find_latest_record(progress_entries, user_id)

    report = {
        'user': user or {'name': 'Student'},
        'target_role': (plan_record.get('plan', {}) if plan_record else {}).get('target_role') or 'Data Analyst',
        'career_readiness_estimate': (plan_record.get('plan', {}) if plan_record else {}).get('readiness_estimate', {}).get('score', 76),
        'resume_analysis': resume_record.get('analysis') if resume_record else {},
        'progress': progress_record if progress_record else {'completed_days': [], 'progress': 0},
        'career_plan': (plan_record.get('plan') if plan_record else {}) or {},
    }
    return success_response({'report': report})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
