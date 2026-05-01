from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Job, JobSeekerProfile, Skill, Category

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    phone = forms.CharField(max_length=15, required=False)
    resume = forms.FileField(required=False, help_text="Upload your CV (Optional)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone', 'email')

class JobForm(forms.ModelForm):
    required_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        required=True
    )
    
    class Meta:
        model = Job
        fields = ['title', 'category', 'description', 'location', 'salary', 'required_skills']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Software Engineer'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe the role...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote, New York'}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. $100k - $120k'}),
        }

class SeekerProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        required=False
    )
    
    class Meta:
        model = JobSeekerProfile
        fields = ['skills', 'resume', 'bio']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }
