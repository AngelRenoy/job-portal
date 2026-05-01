from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),
    path('register/', views.register, name='register'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/jobs/', views.admin_jobs, name='admin_jobs'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/delete-user/<int:pk>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-dashboard/approve-recruiter/<int:pk>/', views.toggle_recruiter_approval, name='toggle_recruiter_approval'),
    path('admin-dashboard/add-recruiter/', views.admin_add_recruiter, name='admin_add_recruiter'),
    path('admin-dashboard/reports/', views.admin_reports, name='admin_reports'),
    path('admin-dashboard/settings/', views.admin_settings, name='admin_settings'),
    path('admin-dashboard/delete-job/<int:pk>/', views.admin_delete_job, name='admin_delete_job'),
    path('approve-job/<int:pk>/', views.approve_job, name='approve_job'),
    path('toggle-user/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
    
    # Recruiter
    path('recruiter-dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('edit-job/<int:pk>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:pk>/', views.delete_job, name='delete_job'),
    path('job/<int:pk>/applicants/', views.view_applicants, name='view_applicants'),
    path('application/<int:pk>/status/', views.update_app_status, name='update_app_status'),
    
    # Job Seeker
    path('seeker-dashboard/', views.seeker_dashboard, name='seeker_dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
]
