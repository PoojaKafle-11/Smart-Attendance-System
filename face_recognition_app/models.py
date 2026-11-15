from django.db import models
from students.models import Student


class FaceProfile(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='face_profile'
    )

    face_encoding = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Face Profile - {self.student.name}"