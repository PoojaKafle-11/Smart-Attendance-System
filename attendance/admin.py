from django.contrib import admin
from .models import AttendanceSession, Attendance


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'class_obj',
        'date',
        'start_time',
        'end_time',
        'status'
    )

    list_filter = (
        'date',
        'status'
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'session',
        'status',
        'marked_at',
        'confidence'
    )

    list_filter = (
        'status',
        'marked_at'
    )

    search_fields = (
        'student__name',
        'student__student_id'
    )
