from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Job, Category, Skill, JobSeekerProfile, Application
from .forms import CustomUserCreationForm, JobForm, SeekerProfileForm
from django.db.models import Count
import PyPDF2
import docx
import re

# Helper function for Resume Parsing
def extract_skills_from_resume(file):
    text = ""
    try:
        if file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        elif file.name.endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error parsing file: {e}")
        return []

    # Clean text
    text = text.lower()
    
    # Get all available skills from DB
    all_skills = Skill.objects.all()
    found_skills = []
    
    for skill in all_skills:
        # Simple word match (boundary aware)
        pattern = r'\b' + re.escape(skill.name.lower()) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill)
            
    return found_skills

# Helper function for Skill Gap Analysis
def analyze_skills(user_skills, job_skills):
    # Convert to sets of names for easier comparison if they are QuerySets
    user_skill_names = set(s.name for s in user_skills)
    job_skill_names = set(s.name for s in job_skills)
    
    matching = user_skill_names.intersection(job_skill_names)
    missing = job_skill_names.difference(user_skill_names)
    
    suggestions = {
        'Python': {'title': 'Python for Everybody', 'link': 'https://www.coursera.org/specializations/python'},
        'Django': {'title': 'Django for Beginners', 'link': 'https://djangoforbeginners.com/'},
        'MySQL': {'title': 'MySQL Crash Course', 'link': 'https://www.mysqltutorial.org/'},
        'JavaScript': {'title': 'Modern JavaScript', 'link': 'https://javascript.info/'},
        'Bootstrap': {'title': 'Bootstrap 5 Guide', 'link': 'https://getbootstrap.com/'},
        'React': {'title': 'React Documentation', 'link': 'https://react.dev/'},
        'HTML': {'title': 'HTML & CSS Basics', 'link': 'https://www.w3schools.com/html/'},
        'CSS': {'title': 'CSS Full Course', 'link': 'https://web.dev/learn/css/'},
        'SQL': {'title': 'SQL Mastery', 'link': 'https://sqlzoo.net/'},
        'PHP': {'title': 'PHP for Beginners', 'link': 'https://www.php.net/manual/en/tutorial.php'},
        'Java': {'title': 'Java Programming', 'link': 'https://dev.java/learn/'},
        'default': {'title': 'Skill Development', 'link': 'https://www.coursera.org/search?query='}
    }
    
    missing_with_resources = []
    for skill_name in missing:
        res = suggestions.get(skill_name, {'title': f"Learn {skill_name}", 'link': f"{suggestions['default']['link']}{skill_name}"})
        missing_with_resources.append({'name': skill_name, 'link': res['link'], 'title': res['title']})
        
    return matching, missing_with_resources

# Public Views
def home(request):
    jobs = Job.objects.filter(is_approved=True).order_by('-created_at')[:6]
    return render(request, 'portal/home.html', {'jobs': jobs})

@login_required
def dashboard_redirect(request):
    if request.user.role == User.IS_ADMIN:
        return redirect('admin_dashboard')
    elif request.user.role == User.IS_RECRUITER:
        return redirect('recruiter_dashboard')
    else:
        return redirect('seeker_dashboard')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        resume = request.FILES.get('resume')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.role = role
            user.phone = phone
            user.save()
            
            # Create profile for job seekers
            if role == User.IS_JOB_SEEKER:
                JobSeekerProfile.objects.create(user=user)
            
            login(request, user)
            messages.success(request, f"Welcome, {username}! Your account has been created.")
            return redirect('home')
            
    return render(request, 'registration/register.html')

# Admin Views
@login_required
def admin_dashboard(request):
    if request.user.role != User.IS_ADMIN:
        return redirect('home')
    
    stats = {
        'total_users': User.objects.exclude(role='admin').count(),
        'total_jobs': Job.objects.count(),
        'total_apps': Application.objects.count(),
        'pending_recruiters': User.objects.filter(role=User.IS_RECRUITER, is_approved=False).count(),
        'pending_jobs': Job.objects.filter(is_approved=False).count(),
    }
    recent_jobs = Job.objects.all().order_by('-created_at')[:5]
    recent_users = User.objects.exclude(role='admin').order_by('-date_joined')[:5]
    
    from django.utils import timezone
    return render(request, 'portal/admin_dashboard.html', {
        'stats': stats, 
        'recent_jobs': recent_jobs, 
        'recent_users': recent_users,
        'today': timezone.now()
    })

@login_required
def admin_jobs(request):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'portal/admin_jobs.html', {'jobs': jobs})

@login_required
def admin_users(request):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    users = User.objects.exclude(role='admin').order_by('-date_joined')
    pending_recruiters = User.objects.filter(role=User.IS_RECRUITER, is_approved=False)
    return render(request, 'portal/admin_users.html', {
        'users': users,
        'pending_recruiters': pending_recruiters
    })

@login_required
def admin_delete_job(request, pk):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    job = get_object_or_404(Job, pk=pk)
    messages.success(request, f"Job '{job.title}' deleted successfully.")
    job.delete()
    return redirect('admin_jobs')

@login_required
def admin_reports(request):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    data = {
        'jobs_by_cat': Category.objects.annotate(count=Count('job')),
        'apps_by_status': Application.objects.values('status').annotate(count=Count('id'))
    }
    return render(request, 'portal/admin_reports.html', {'data': data})

@login_required
def admin_settings(request):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    return render(request, 'portal/admin_settings.html')

@login_required
def admin_delete_user(request, pk):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        messages.error(request, "You cannot delete yourself.")
    else:
        messages.success(request, f"User {u.username} has been deleted.")
        u.delete()
    return redirect('admin_users')

@login_required
def admin_add_recruiter(request):
    if request.user.role != User.IS_ADMIN: return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.role = User.IS_RECRUITER
            user.phone = phone
            user.save()
            messages.success(request, f"Recruiter {username} has been added successfully.")
            return redirect('admin_users')
    
    return render(request, 'portal/admin_add_recruiter.html')

@login_required
def approve_job(request, pk):
    if request.user.role == User.IS_ADMIN:
        job = get_object_or_404(Job, pk=pk)
        job.is_approved = True
        job.save()
        messages.success(request, f"Job '{job.title}' approved.")
    return redirect('admin_dashboard')

@login_required
def toggle_user_status(request, pk):
    if request.user.role == User.IS_ADMIN:
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.info(request, f"User {user.username} has been {status}.")
    return redirect('admin_dashboard')

@login_required
def toggle_recruiter_approval(request, pk):
    if request.user.role == User.IS_ADMIN:
        user = get_object_or_404(User, pk=pk)
        user.is_approved = not user.is_approved
        user.save()
        status = "Approved" if user.is_approved else "Disapproved"
        messages.success(request, f"Recruiter {user.username} is now {status}.")
    return redirect('admin_users')

# Recruiter Views
@login_required
def recruiter_dashboard(request):
    if request.user.role != User.IS_RECRUITER:
        return redirect('home')
    
    my_jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'portal/recruiter_dashboard.html', {'jobs': my_jobs})

@login_required
def post_job(request):
    if request.user.role != User.IS_RECRUITER:
        return redirect('home')
    
    if not request.user.is_approved:
        messages.warning(request, "Your recruiter account is pending administrator approval. You can post jobs once approved.")
        return redirect('recruiter_dashboard')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            form.save_m2m()
            messages.success(request, "Job posted successfully. Waiting for admin approval.")
            return redirect('recruiter_dashboard')
    else:
        form = JobForm()
    return render(request, 'portal/job_form.html', {'form': form, 'title': 'Post a New Job'})

@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect('recruiter_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'portal/job_form.html', {'form': form, 'title': f'Edit Job: {job.title}'})

@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('recruiter_dashboard')

@login_required
def view_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    apps = job.applications.all()
    return render(request, 'portal/applicants.html', {'job': job, 'apps': apps})

from django.http import JsonResponse

@login_required
def update_app_status(request, pk):
    if request.method == 'POST':
        app = get_object_or_404(Application, pk=pk, job__posted_by=request.user)
        status = request.POST.get('status')
        if status in ['applied', 'reviewed', 'shortlisted', 'accepted', 'rejected']:
            app.status = status
            app.save()
            messages.success(request, f"Application status updated to {status.capitalize()}.")
        else:
            messages.error(request, "Invalid status provided.")
        return redirect('view_applicants', pk=app.job.pk)
    return redirect('recruiter_dashboard')

# Job Seeker Views
@login_required
def seeker_dashboard(request):
    if request.user.role != User.IS_JOB_SEEKER:
        return redirect('home')
    
    my_apps = Application.objects.filter(seeker=request.user)
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    
    # Calculate Completion %
    completion = 40 # Base for registration
    if request.user.phone: completion += 10
    if profile.bio: completion += 15
    if profile.resume: completion += 20
    if profile.skills.exists(): completion += 15
    
    return render(request, 'portal/seeker_dashboard.html', {
        'apps': my_apps, 
        'profile': profile,
        'completion': completion
    })

@login_required
def update_profile(request):
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = SeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'resume' in request.FILES:
                new_skills = extract_skills_from_resume(request.FILES['resume'])
                if new_skills:
                    # Clear existing skills and add new ones (or just add)
                    # For now, let's just add to existing
                    profile.save() # Save profile first
                    profile.skills.add(*new_skills)
                    messages.info(request, f"Extracted {len(new_skills)} skills from your resume!")
            
            profile.save()
            form.save_m2m() # Save ManyToMany fields (skills)
            messages.success(request, "Profile updated successfully.")
            return redirect('seeker_dashboard')
    else:
        form = SeekerProfileForm(instance=profile)
    return render(request, 'portal/profile_form.html', {'form': form})

def job_list(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    category = request.GET.get('category')
    
    jobs = Job.objects.all().order_by('-created_at')
    
    if query:
        jobs = jobs.filter(title__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if category:
        jobs = jobs.filter(category_id=category)
        
    categories = Category.objects.all()
    return render(request, 'portal/job_list.html', {'jobs': jobs, 'categories': categories})

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = Application.objects.filter(job=job, seeker=request.user).exists()
    
    analysis = None
    if request.user.role == User.IS_JOB_SEEKER:
        # Ensure profile exists
        profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
        user_skills = set(profile.skills.all())
        job_skills = set(job.required_skills.all())
        
        matching, missing = analyze_skills(user_skills, job_skills)
        score = 0
        if job_skills:
            score = int((len(matching) / len(job_skills) * 100))
        else:
            score = 100 # No requirements means 100% match
            
        analysis = {
            'matching': matching,
            'missing': missing,
            'score': score,
            'weight_per_skill': int(100 / len(job_skills)) if job_skills else 0
        }
        
    return render(request, 'portal/job_detail.html', {
        'job': job, 
        'has_applied': has_applied,
        'analysis': analysis
    })

@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.user.role == User.IS_JOB_SEEKER:
        profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            resume = request.FILES.get('resume')
            
            # Use profile resume if no new resume is uploaded
            if not resume:
                resume = profile.resume
                
            if not resume:
                messages.error(request, "Please upload your CV in your profile or here to apply.")
                return redirect('job_detail', pk=pk)
            
            if not Application.objects.filter(job=job, seeker=request.user).exists():
                Application.objects.create(job=job, seeker=request.user, resume=resume)
                messages.success(request, "Successfully applied for the job!")
            else:
                messages.warning(request, "You have already applied for this job.")
        else:
            return redirect('job_detail', pk=pk)
    return redirect('job_detail', pk=pk)
