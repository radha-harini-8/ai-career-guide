# AI Career Guide & Resume Analyzer

A student-friendly full-stack Flask application that helps users plan their career, identify skill gaps, create learning roadmaps, analyze resumes, evaluate ATS compatibility, compare resumes to job descriptions, and prepare for interviews.

## Features

- AI-powered career guidance and personalized 30-day learning plans
- Resume analysis and ATS compatibility estimates
- Resume-to-job match scoring
- Job description extraction and skill matching
- Interview preparation with technical, HR, and behavioral questions
- Learning resource suggestions, project recommendations, and certifications
- JSON-based persistence for users, plans, progress, and reports
- Orange and white responsive UI built with Flask + vanilla JavaScript

## Technology Stack

- Python 3.x
- Flask
- HTML5, CSS3, JavaScript
- Google Gemini API
- JSON storage
- PDF, DOCX, and TXT resume parsing

## Project Architecture

- `app.py` – Flask app and route definitions
- `utils/gemini.py` – Gemini integration and fallback logic
- `utils/resume_parser.py` – Resume extraction and validation
- `utils/ats_analyzer.py` – ATS compatibility calculations
- `utils/json_storage.py` – JSON persistence helpers
- `templates/` – HTML pages
- `static/` – CSS and JavaScript assets
- `data/` – JSON storage files
- `uploads/` – Uploaded resume files

## Installation

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API key

Create a `.env` file in the project root and add:

```env
GEMINI_API_KEY=your_api_key_here
```

You can copy `.env.example` as a starting point.

## Run the Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Folder Structure

```text
project/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── data/
│   ├── users.json
│   ├── career_plans.json
│   ├── resume_analysis.json
│   ├── job_analysis.json
│   ├── progress.json
│   └── interview_sessions.json
├── templates/
│   ├── index.html
│   ├── career-guide.html
│   ├── resume-analyzer.html
│   ├── job-analyzer.html
│   ├── interview-prep.html
│   ├── dashboard.html
│   └── report.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── career.js
│   │   ├── resume.js
│   │   ├── jobs.js
│   │   ├── interview.js
│   │   └── dashboard.js
│   └── images/
├── uploads/
├── utils/
│   ├── gemini.py
│   ├── resume_parser.py
│   ├── ats_analyzer.py
│   └── json_storage.py
└── venv/
```

## JSON Storage

The app uses simple JSON files for persistence instead of a database:

- `users.json` – user profile data
- `career_plans.json` – AI-generated career plans
- `resume_analysis.json` – resume analysis records
- `job_analysis.json` – job description analysis records
- `progress.json` – daily learning progress
- `interview_sessions.json` – interview records

## Resume Uploads

Uploaded resumes are validated for:

- file type
- file size
- empty content
- corrupt or unreadable data

Files are saved under the `uploads/` directory outside public static folders for security.

## Gemini Integration

The application keeps the Gemini API key in a `.env` file and calls Gemini only from the Python backend. Frontend JavaScript never receives the API key. If the key is unavailable or the API fails, the app uses a safe fallback analysis so the system still works locally.

## API Routes

- `GET /` – landing page
- `GET /career-guide` – AI career guide page
- `GET /resume-analyzer` – resume analyzer page
- `GET /job-analyzer` – job description analyzer page
- `GET /interview-prep` – interview prep page
- `GET /dashboard` – dashboard page
- `POST /api/career-plan`
- `POST /api/analyze-resume`
- `POST /api/analyze-job`
- `POST /api/match-resume`
- `POST /api/interview`
- `POST /api/projects`
- `POST /api/certifications`
- `POST /api/progress`
- `GET /api/dashboard/<user_id>`
- `GET /api/resources`

## Future Improvements

- Add authentication
- Add report PDF export with reportlab
- Add more job portals and scraping support
- Expand role-specific career intelligence
- Add historical trend charts and analytics

## Notes

This project is designed to be beginner-friendly, practical, and demonstrable for a B.Tech final-year project.
