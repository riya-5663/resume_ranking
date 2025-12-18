import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import logging
from collections import namedtuple
from nltk.corpus import stopwords
from .models import Job, Resume
import pdfplumber

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.word_tokenize("test")
except LookupError:
    nltk.download("punkt")

ResumeData =namedtuple("ResumeData",["file_path","structured_data","score","details","user"])
JobRequirements = namedtuple("JobRequirements", ["required_skills", "preferred_skills", "min_experience", "education", "responsibilities", "keywords"])

PREDEFINED_SKILLS = [
    # Programming Languages
    "python", "java", "c++", "c", "c#", "javascript", "typescript", "go", "ruby", "swift",
    "kotlin", "php", "r", "scala", "perl", "bash", "matlab", "sql", "html", "css", "assembly",

    # Web Development
    "react", "angular", "vue", "django", "flask", "node.js", "express.js", "next.js",
    "bootstrap", "jquery", "tailwind css", "sass", "webpack",

    # Mobile Development
    "android", "ios", "react native", "flutter", "xamarin",

    # Data Science & Machine Learning
    "machine learning", "deep learning", "data analysis", "data visualization",
    "pandas", "numpy", "scikit-learn", "tensorflow", "keras", "pytorch",
    "matplotlib", "seaborn", "xgboost", "lightgbm", "opencv", "nlp", "transformers",

    # Cloud Platforms
    "aws", "azure", "google cloud", "gcp", "digitalocean", "heroku", "cloudflare",

    # DevOps & Infrastructure
    "docker", "kubernetes", "jenkins", "ansible", "terraform", "linux", "shell scripting",
    "prometheus", "grafana", "nagios", "ci/cd", "git", "github", "gitlab", "bitbucket",

    # Databases & Big Data
    "mysql", "postgresql", "mongodb", "oracle", "sqlite", "redis", "firebase",
    "cassandra", "hadoop", "spark", "hive", "snowflake", "bigquery", "data warehouse",

    # BI / Analytics Tools
    "excel", "power bi", "tableau", "looker", "qlikview", "sas", "google analytics",

    # Testing
    "unit testing", "selenium", "jest", "mocha", "junit", "pytest", "postman", "cypress",

    # Soft Skills
    "communication", "leadership", "teamwork", "problem solving", "time management",
    "critical thinking", "adaptability", "collaboration", "attention to detail",

    # Project Management & Methodologies
    "agile", "scrum", "kanban", "jira", "trello", "asana", "confluence", "project management",
    "waterfall", "product owner", "stakeholder management"
]


def extract_text_from_pdf(pdf_path):
    data={"full_text":"","experience":0,"education":[],"skills":[],"projects":[]}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text=""
            for page in pdf.pages:
                full_text+=page.extract_text()
            data["full_text"]=full_text
            data["experience"]=extract_experience(full_text)
            data["education"]=extract_education(full_text)
            data["skills"]=extract_skills(full_text)
            data["projects"]=extract_projects(full_text)

    except Exception as e:
        print(f"Error extracting text from PDF:{e}")
    return data    

def extract_experience(text):
    years=0
    experience_keywords=[
        r"\b(\d+)\s*(years?|yrs?|y)\s*of\s*experience\b", 
        r"\b(\d{4})\s*-\s*(\d{4})\b", 
        r"\bworked\s*as\s*(\w+)\b", 
        r"\b(\d+)\s*year\s*experience\b", 
    ]    
    for pattern in experience_keywords:
        for match in re.findall(pattern, text.lower()):
            if isinstance(match, tuple) and all(item.isdigit() for item in match):
                diff = int(match[1]) - int(match[0])
                if diff > years:
                    years = diff
            elif isinstance(match, str) and match.isdigit():
                years = max(years, int(match))
    return years

def extract_education(text):
     degrees = [
        "bachelor", "master", "phd", "doctorate", "associate", "diploma", "certification"
    ]
     
     institutions = [
        "university", "college", "institute", "academy", "school", "academy"
    ]
     eduaction_matches=[]
     eduaction_keywords= [
        r"\b(bachelor's|bachelor)\s*degree\b", 
        r"\b(master's|master)\s*degree\b",  
        r"\bphd\b",  
        r"\bdoctorate\b",  
        r"\b(\d{4})\s*-*\s*(\d{4})\b",  
        r"\b([A-Za-z\s]+)\s*(university|college|institute|academy)\b", 
    ]
     
     for pattern in eduaction_keywords:
         matches=re.findall(pattern,text.lower())
         if matches:
             eduaction_matches.extend(matches)
    
     education_details=[]
     for match in eduaction_matches:
         if isinstance(match,tuple) and len(match)==2:
            degree,institution=match
            institution=institution.capitalize()
            education_details.append(f"{degree.title()} at {institution}")
         elif isinstance(match, str):
            education_details.append(match.title())

     return education_details

def extract_skills(text):
    skill_set=PREDEFINED_SKILLS
    found_skills = set()
    text_lower = text.lower()

    for skill in skill_set:
        skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(skill_pattern, text_lower):
            found_skills.add(skill.lower())

    return list(found_skills)

def extract_projects(text):
    text_lower = text.lower()
    action_keywords = [
        "developed", "implemented", "built", "designed", "engineered", "launched", 
        "created", "worked on", "led", "optimized", "deployed", "automated"
    ]

    paragraphs = re.split(r'\n{2,}', text_lower)
    projects = []

    for para in paragraphs:
        if any(action in para for action in action_keywords):
            cleaned_para = re.sub(r'\s+', ' ', para).strip()
            if 10 < len(cleaned_para) < 1000:  
                projects.append(cleaned_para)

    return list(set(projects)) 


def process_skills(skills_text):
    if not skills_text:
        return[]
    return  [skill.strip().lower() for skill in skills_text.split(',')]

def parse_experience(experience_text):
    if not experience_text:
        return 0
    experience_map={
        "entry":1,
        "junior": 2,
        "mid": 3,
        "senior": 5,
        "lead": 7,
        "manager": 10
    }
    experience_text=experience_text.lower()
    for key,value in experience_map.items():
        if key in experience_text:
            return value
    return 0

def parse_responsibilities(responsibilities_text):
    if not responsibilities_text:
        return []
    return [resp.strip() for resp in responsibilities_text.split('\n') if resp.strip()]

def extract_keywords_from_description(description_text):
    if not description_text:
        return []
    words=re.findall(r'\b\w+\b', description_text.lower())
    stop_words = set(stopwords.words("english"))
    keywords = [word for word in words if word not in stop_words]
    return list(set(keywords)) 

def extract_job_requirements(job_id):
    try:
        job=Job.objects.get(id=job_id)

        return JobRequirements(
            required_skills=process_skills(job.required_skills),
            preferred_skills=process_skills(job.preferred_skills),
            min_experience=parse_experience(job.experience_level),
            education=job.education_requirements,
            responsibilities=parse_responsibilities(job.responsibilities),
            keywords=extract_keywords_from_description(job.description)

        )
    except Job.DoesNotExist:
        print(f"Job with ID {job_id} not found.")
        return None

def calculate_project_score(resume_projects, job_description_keywords):
    if not resume_projects or not job_description_keywords:
        return 0
    project_score=0
    matched_keywords=set()
    for resume_project in resume_projects:
        matched_keywords.update(set(keyword for keyword in job_description_keywords if keyword in resume_project))
    project_score=len(matched_keywords)

    normalized_project_score = project_score / max(1, len(job_description_keywords))
    
    return normalized_project_score * 10

def calculate_tfidf_similarity(text1, text2):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]


def calculate_resume_score(resume_data, job_requirements):
    if not resume_data or not job_requirements or not isinstance(job_requirements,JobRequirements):
        return 0
    
    resume_full_text_lower=resume_data.get("full_text","").lower()
    resume_skills_lower=[skill.lower() for skill in resume_data.get("skills",[])]
    resume_projects_lower=[project.lower() for project in resume_data.get("projects",[])]

    score={
        "required_skills":0,
        "preferred_skill":0,
        "experience":0,
        "education":0,
        "job_description":0,
        "projects":0,
    }

    required_skill_matches=sum(1 for skill in job_requirements.required_skills if skill.lower() in resume_skills_lower)
    score["required_skills"]=(required_skill_matches/max(1,len(job_requirements.required_skills)))*30

    preferred_skill_matches=sum(1 for skill in job_requirements.preferred_skills if skill.lower() in resume_skills_lower)
    score["preferred_skill"]=(preferred_skill_matches/max(1,len(job_requirements.preferred_skills)))*20

    resume_experience=resume_data.get("experience",0)
    if resume_experience>=job_requirements.min_experience:
        score["experience"]=(resume_experience-job_requirements.min_experience)*5
    else: 
        score["experience"]=10

    education_match = any(job_requirements.education.lower() in edu.lower() for edu in resume_data.get("education", []))
    score["education"]=education_match*10

    job_keywords=''.join(job_requirements.keywords)
    resume_keywords=resume_data.get("full_text","")
    tfidf_score=calculate_tfidf_similarity(resume_keywords,job_keywords)
    score["job_description"]=tfidf_score*25

    project_score=calculate_project_score(resume_projects_lower,job_requirements.keywords)
    score["projects"]=project_score*15


    total_score=sum(score.values())
    return total_score,score

def rank_resumes(job_id):
    try:
        job=Job.objects.get(id=job_id)

    except Job.DoesNotExist:
        print(f"Job with ID {job_id} not found.")
        return []
    
    job_description_text=job.description

    if not job_description_text:
         print("Error: Job description text is missing.")
         return []
    
    job_requirements=extract_job_requirements(job_id)

    resume_scores=[]

    resumes=Resume.objects.filter(job=job)

    for resume in resumes:
        extracted_data=extract_text_from_pdf(resume.file.path)
        if extracted_data:
            total_score, _=calculate_resume_score(extracted_data,job_requirements)
            resume.score=total_score
            resume.save()
            resume_scores.append(ResumeData(resume.file.path,extracted_data,total_score,resume,resume.user.username))

    ranked_resumes=sorted(resume_scores,key=lambda x: x.score,reverse=True)

    return ranked_resumes            

