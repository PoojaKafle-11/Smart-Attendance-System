from django.db import models
from academics.models import Class


class AttendanceSession(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    GRACE_PERIOD_CHOICES = [
        (0, 'No grace period'),
        (5, '5 minutes'),
        (10, '10 minutes'),
        (15, '15 minutes'),
        (20, '20 minutes'),
        (30, '30 minutes'),
    ]

    grace_period = models.PositiveSmallIntegerField(
        choices=GRACE_PERIOD_CHOICES,
        default=10
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_obj} - {self.date}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    marked_at = models.DateTimeField(auto_now_add=True)

    confidence = models.FloatField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'student'],
                name='unique_student_attendance_per_session'
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.status}"
