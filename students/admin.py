from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'name',
        'email',
        'semester',
        'section',
        'created_at'
    )

    search_fields = (
        'student_id',
        'name',
        'email'
    )

    list_filter = (
        'semester',
        'section'
    )
