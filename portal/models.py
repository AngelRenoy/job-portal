from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    IS_ADMIN = 'admin'
    IS_JOB_SEEKER = 'job_seeker'
    IS_RECRUITER = 'recruiter'
    
    ROLE_CHOICES = (
        (IS_ADMIN, 'Admin'),
        (IS_JOB_SEEKER, 'Job Seeker'),
        (IS_RECRUITER, 'Recruiter'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=IS_JOB_SEEKER)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Job(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=100, blank=True, null=True)
    required_skills = models.ManyToManyField(Skill, related_name='jobs')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seeker_profile')
    skills = models.ManyToManyField(Skill, related_name='seekers')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_applications')
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seeker.username} - {self.job.title}"
