from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    total_topics = models.IntegerField(default=0)
    completed_topics = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def pending_topics(self):
        pending = self.total_topics - self.completed_topics
        return pending if pending > 0 else 0

    def __str__(self):
        return self.name


class StudyAvailability(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    monday_hours = models.FloatField(default=0)
    tuesday_hours = models.FloatField(default=0)
    wednesday_hours = models.FloatField(default=0)
    thursday_hours = models.FloatField(default=0)
    friday_hours = models.FloatField(default=0)
    saturday_hours = models.FloatField(default=0)
    sunday_hours = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} Availability"


class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date = models.DateField()

    def __str__(self):
        return f"{self.subject.name} - {self.exam_date}"