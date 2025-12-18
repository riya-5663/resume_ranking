from django.shortcuts import render, redirect, get_object_or_404
from .models import Resume, Job
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ResumeForm
from .rank_resume import (
    extract_text_from_pdf,
    calculate_resume_score,
    extract_job_requirements,
    rank_resumes,
)

def logout_view(request):
    logout(request)
    return redirect('signup')

def login_view(request):
    context = {}

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            context['form'] = form
            context['error'] = "Invalid credentials."
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form, 'active_tab': 'login'})

def signup_view(request):
    context = {}

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            context['form'] = form
            context['error'] = "There was an error with your signup details."
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form, 'active_tab': 'signup'})

@login_required
def dashboard_view(request):
    user = request.user
    resumes = Resume.objects.filter(user=user)
    jobs = Job.objects.all()
    return render(request, 'dashboard.html', {
        'user': user,
        'jobs': jobs,
        'resumes': resumes,
        'active_tab': 'dashboard'})

@login_required
def upload_resume(request):
    user = request.user
    jobs = Job.objects.all()

    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        job_id = request.POST.get('job_id') 
        if job_id:
            job = get_object_or_404(Job, id=job_id)
        else:
            print("Job ID not found")

        if form.is_valid() and job_id:
            job = get_object_or_404(Job, id=job_id)
            resume = form.save(commit=False)
            resume.user = user
            resume.job = job
            resume.save()

            # Extract text from the uploaded PDF
            file_path = resume.file.path
            structured_data = extract_text_from_pdf(file_path)

            if not structured_data:
                return render(request, 'upload_resume.html', {
                    'form': form,
                    'jobs': jobs,
                    'error': "Failed to extract text from resume.",
                    'active_tab': 'upload'
                })

            job_requirements = extract_job_requirements(job.id)
            total_score, breakdown = calculate_resume_score(structured_data, job_requirements)

            resume.score = total_score
            resume.save()

            ranked_resumes = rank_resumes(job.id)
            resume_rank = next((i for i, r in enumerate(ranked_resumes) if r.file_path == resume.file.path), None)

            return render(request, 'upload_resume.html', {
                'resume': resume,
                'user': user,
                'job': job,
                'score': total_score,
                'score_breakdown': breakdown,
                'resume_rank': resume_rank + 1 if resume_rank is not None else "Not ranked",
                'ranked_resumes': ranked_resumes,
                'jobs': jobs,
                'active_tab': 'ranked'  
            })
    else:
        form = ResumeForm(request.POST, request.FILES)

    return render(request, 'upload_resume.html', {
        'form': form,
        'jobs': jobs,
        'active_tab': 'upload'
    })

@login_required
def resume_score_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    job = resume.job
    ranked_resumes = rank_resumes(job.id)

    structured_data = extract_text_from_pdf(resume.file.path)
    job_requirements = extract_job_requirements(job.id)
    total_score, breakdown_scores = calculate_resume_score(structured_data, job_requirements)

    resume_rank = next((index for index, r in enumerate(ranked_resumes) if r.file_path == resume.file.path), None)

    return render(request, 'rank_resume.html', {
        'resume': resume,
        'score': total_score,
        'score_breakdown': breakdown_scores,
        'ranked_resumes': ranked_resumes,
        'resume_rank': resume_rank + 1 if resume_rank is not None else "Not ranked",
        'job': job,
        'jobs': Job.objects.all(),
        'active_tab': 'ranked'  
    })
