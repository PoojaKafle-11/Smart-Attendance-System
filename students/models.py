from django.db import models


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    semester = models.PositiveIntegerField()
    section = models.CharField(max_length=10)

    profile_photo = models.ImageField(
        upload_to='student_profiles/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"
