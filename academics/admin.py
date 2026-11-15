from django.contrib import admin
from .models import Subject, Class


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'semester'
    )

    search_fields = (
        'code',
        'name'
    )

    list_filter = (
        'semester',
    )


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
        'teacher',
        'semester',
        'section',
        'room'
    )

    list_filter = (
        'semester',
        'section'
    )

    search_fields = (
        'subject__name',
        'teacher__name'
    )
