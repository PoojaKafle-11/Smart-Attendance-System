from django.contrib import admin
from .models import FaceProfile


@admin.register(FaceProfile)
class FaceProfileAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'student__name',
        'student__student_id'
    )
