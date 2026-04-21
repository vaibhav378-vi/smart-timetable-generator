from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/delete/<int:id>/', views.delete_subject, name='delete_subject'),
    path('subjects/increment/<int:id>/', views.increment_completed_topic, name='increment_completed_topic'),
    path('subjects/decrement/<int:id>/', views.decrement_completed_topic, name='decrement_completed_topic'),

    path('availability/', views.set_availability, name='set_availability'),
    path('weekly-timetable/', views.generate_timetable, name='generate_timetable'),

    path('exams/', views.exam_list, name='exam_list'),
    path('exams/add/', views.add_exam, name='add_exam'),
    path('exams/delete/<int:id>/', views.delete_exam, name='delete_exam'),

    path('progress-report/', views.progress_report, name='progress_report'),
    path('logout/', views.user_logout, name='logout'),
]