from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True, blank=True)
    required_skills = models.TextField(max_length=2000, null=True, blank=True)  
    preferred_skills = models.TextField(max_length=2000, null=True, blank=True)  
    experience_level = models.CharField(max_length=1000, null=True, blank=True)  
    education_requirements = models.TextField(default="Not specified")  
    responsibilities = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.title

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    text = models.TextField(blank=True)
    score = models.FloatField(default=0.0) 

    def __str__(self):
        return f"Resume for {self.job.title if self.job else 'No Job Selected'}"
    

