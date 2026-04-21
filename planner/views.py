from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Subject, StudyAvailability, Exam


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, 'planner/register.html', {'error': 'Username and password are required'})

        if User.objects.filter(username=username).exists():
            return render(request, 'planner/register.html', {'error': 'Username already exists'})

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'planner/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, 'planner/login.html', {'error': 'Please enter username and password'})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'planner/login.html', {'error': 'Invalid username or password'})

    return render(request, 'planner/login.html')


@login_required
def dashboard(request):
    subjects = Subject.objects.filter(user=request.user)
    subject_count = subjects.count()
    exam_count = Exam.objects.filter(user=request.user).count()

    total_topics_sum = sum(subject.total_topics for subject in subjects)
    completed_topics_sum = sum(subject.completed_topics for subject in subjects)
    pending_topics_sum = sum(subject.pending_topics() for subject in subjects)

    if total_topics_sum > 0:
        overall_progress = round((completed_topics_sum / total_topics_sum) * 100, 1)
    else:
        overall_progress = 0

    return render(request, 'planner/dashboard.html', {
        'subject_count': subject_count,
        'exam_count': exam_count,
        'total_topics_sum': total_topics_sum,
        'completed_topics_sum': completed_topics_sum,
        'pending_topics_sum': pending_topics_sum,
        'overall_progress': overall_progress,
    })


@login_required
def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        priority = request.POST.get('priority', '').strip()
        total_topics = request.POST.get('total_topics', '').strip()
        completed_topics = request.POST.get('completed_topics', '').strip()

        if name and priority and total_topics != '' and completed_topics != '':
            Subject.objects.create(
                user=request.user,
                name=name,
                priority=priority,
                total_topics=int(total_topics),
                completed_topics=int(completed_topics)
            )
            return redirect('subject_list')

        return render(request, 'planner/add_subject.html', {'error': 'Please fill all fields'})

    return render(request, 'planner/add_subject.html')


@login_required
def subject_list(request):
    subjects = Subject.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'planner/subject_list.html', {'subjects': subjects})


@login_required
def delete_subject(request, id):
    subject = get_object_or_404(Subject, id=id, user=request.user)
    subject.delete()
    return redirect('subject_list')


@login_required
def increment_completed_topic(request, id):
    subject = get_object_or_404(Subject, id=id, user=request.user)
    if subject.completed_topics < subject.total_topics:
        subject.completed_topics += 1
        subject.save()
    return redirect('subject_list')


@login_required
def decrement_completed_topic(request, id):
    subject = get_object_or_404(Subject, id=id, user=request.user)
    if subject.completed_topics > 0:
        subject.completed_topics -= 1
        subject.save()
    return redirect('subject_list')


@login_required
def set_availability(request):
    availability, created = StudyAvailability.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        availability.monday_hours = float(request.POST.get('monday_hours', 0) or 0)
        availability.tuesday_hours = float(request.POST.get('tuesday_hours', 0) or 0)
        availability.wednesday_hours = float(request.POST.get('wednesday_hours', 0) or 0)
        availability.thursday_hours = float(request.POST.get('thursday_hours', 0) or 0)
        availability.friday_hours = float(request.POST.get('friday_hours', 0) or 0)
        availability.saturday_hours = float(request.POST.get('saturday_hours', 0) or 0)
        availability.sunday_hours = float(request.POST.get('sunday_hours', 0) or 0)
        availability.save()
        return redirect('generate_timetable')

    return render(request, 'planner/set_availability.html', {'availability': availability})


@login_required
def add_exam(request):
    subjects = Subject.objects.filter(user=request.user).order_by('name')

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        exam_date = request.POST.get('exam_date')

        if subject_id and exam_date:
            subject = get_object_or_404(Subject, id=subject_id, user=request.user)
            Exam.objects.create(user=request.user, subject=subject, exam_date=exam_date)
            return redirect('exam_list')

        return render(request, 'planner/add_exam.html', {
            'subjects': subjects,
            'error': 'Please fill all fields'
        })

    return render(request, 'planner/add_exam.html', {'subjects': subjects})


@login_required
def exam_list(request):
    exams = Exam.objects.filter(user=request.user).order_by('exam_date')
    return render(request, 'planner/exam_list.html', {'exams': exams})


@login_required
def delete_exam(request, id):
    exam = get_object_or_404(Exam, id=id, user=request.user)
    exam.delete()
    return redirect('exam_list')


@login_required
def generate_timetable(request):
    subjects = list(Subject.objects.filter(user=request.user))

    if not subjects:
        return render(request, 'planner/weekly_timetable.html', {
            'timetable': [],
            'message': 'Please add subjects first.'
        })

    try:
        availability = StudyAvailability.objects.get(user=request.user)
    except StudyAvailability.DoesNotExist:
        return render(request, 'planner/weekly_timetable.html', {
            'timetable': [],
            'message': 'Please set your weekly availability first.'
        })

    exams = {exam.subject_id: exam for exam in Exam.objects.filter(user=request.user)}

    days = [
        ('Monday', availability.monday_hours),
        ('Tuesday', availability.tuesday_hours),
        ('Wednesday', availability.wednesday_hours),
        ('Thursday', availability.thursday_hours),
        ('Friday', availability.friday_hours),
        ('Saturday', availability.saturday_hours),
        ('Sunday', availability.sunday_hours),
    ]

    from datetime import date
    today = date.today()
    weighted_subjects = []

    for subject in subjects:
        pending = subject.pending_topics()
        if pending <= 0:
            continue

        if subject.priority == 'High':
            priority_weight = 3
        elif subject.priority == 'Medium':
            priority_weight = 2
        else:
            priority_weight = 1

        base_weight = pending * priority_weight
        exam_boost = 0
        exam = exams.get(subject.id)
        exam_info = 'No exam added'

        if exam:
            days_left = (exam.exam_date - today).days
            exam_info = f"Exam on {exam.exam_date}"

            if days_left <= 3:
                exam_boost = 6
            elif days_left <= 7:
                exam_boost = 4
            elif days_left <= 15:
                exam_boost = 2
            else:
                exam_boost = 1

        final_weight = base_weight + exam_boost
        weighted_subjects.append({
            'name': subject.name,
            'weight': final_weight,
            'exam_info': exam_info,
        })

    if not weighted_subjects:
        return render(request, 'planner/weekly_timetable.html', {
            'timetable': [],
            'message': 'All subjects look completed. Great work!'
        })

    total_weight = sum(item['weight'] for item in weighted_subjects)
    timetable = []

    for day_name, total_hours in days:
        day_plan = []

        if total_hours > 0:
            for item in weighted_subjects:
                allocated_hours = round((item['weight'] / total_weight) * total_hours, 1)
                if allocated_hours > 0:
                    day_plan.append({
                        'subject': item['name'],
                        'hours': allocated_hours,
                        'exam_info': item['exam_info']
                    })

            day_plan.sort(key=lambda x: x['hours'], reverse=True)

        timetable.append({
            'day': day_name,
            'total_hours': total_hours,
            'plan': day_plan
        })

    return render(request, 'planner/weekly_timetable.html', {
        'timetable': timetable,
        'message': ''
    })


@login_required
def progress_report(request):
    subjects = Subject.objects.filter(user=request.user).order_by('name')

    subject_reports = []
    total_topics_sum = 0
    completed_topics_sum = 0
    pending_topics_sum = 0

    for subject in subjects:
        total_topics = subject.total_topics
        completed_topics = subject.completed_topics
        pending_topics = subject.pending_topics()

        if total_topics > 0:
            progress_percent = round((completed_topics / total_topics) * 100, 1)
        else:
            progress_percent = 0

        subject_reports.append({
            'name': subject.name,
            'priority': subject.priority,
            'total_topics': total_topics,
            'completed_topics': completed_topics,
            'pending_topics': pending_topics,
            'progress_percent': progress_percent,
        })

        total_topics_sum += total_topics
        completed_topics_sum += completed_topics
        pending_topics_sum += pending_topics

    if total_topics_sum > 0:
        overall_progress = round((completed_topics_sum / total_topics_sum) * 100, 1)
    else:
        overall_progress = 0

    return render(request, 'planner/progress_report.html', {
        'subject_reports': subject_reports,
        'total_topics_sum': total_topics_sum,
        'completed_topics_sum': completed_topics_sum,
        'pending_topics_sum': pending_topics_sum,
        'overall_progress': overall_progress,
    })


def user_logout(request):
    logout(request)
    return redirect('login')