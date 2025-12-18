Resume Ranking System
Overview

The Resume Ranking System is a Django-based web application that automates the process of screening and ranking resumes. It allows users to upload resumes, analyzes them using predefined logic, and produces ranked results to support recruitment and shortlisting decisions.

This repository is structured and documented for local development as well as production deployment.


Features

User registration and authentication

Resume upload and storage

Automated resume ranking logic

Result visualization through web interface

Django Admin dashboard for management

Production-ready configuration support

Tech Stack

Backend: Python 3, Django

Frontend: HTML, CSS, JavaScript

Database: SQLite (development), PostgreSQL-ready (production)

Dependency Management: Pipenv

Static Handling: Django Staticfiles

Deployment Ready: Gunicorn-compatible

Project Structure
resume_ranking/
│
├── manage.py
├── db.sqlite3
├── Pipfile
├── Pipfile.lock
│
├── resume_ranking/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── resumechecker/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── rank_resume.py
│   └── tests.py
│
├── templates/
├── static/
├── staticfiles/
├── media/
│   └── resumes/
└── README.md

Environment Setup (Local)
1. Clone the Repository
git clone https://github.com/your-username/resume-ranking.git
cd resume-ranking

2. Create Virtual Environment & Install Dependencies
pip install pipenv
pipenv install
pipenv shell

3. Environment Variables

Create a .env file in the root directory:

DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost


In production, set DEBUG=False and update ALLOWED_HOSTS.

4. Database Migrations
python manage.py migrate

5. Create Admin User
python manage.py createsuperuser

6. Collect Static Files
python manage.py collectstatic

7. Run Development Server
python manage.py runserver


Access the application at:

http://127.0.0.1:8000/

The app is compatible with PostgreSQL.

Example (settings.py):

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dbname',
        'USER': 'dbuser',
        'PASSWORD': 'dbpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

Security Considerations

Do not commit .env files

Rotate SECRET_KEY in production

Use HTTPS in deployment

Restrict Django Admin access

Future Improvements

NLP/ML-based resume scoring

Role-based job descriptions

Resume parsing (PDF/DOCX)

Cloud storage for resumes

CI/CD integration

Contributors
Pratishtha,
Riya
