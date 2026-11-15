
from django.urls import path
from . import views

urlpatterns = [

    path('create/', views.create_session, name='create_session'),

    path('sessions/', views.session_list, name='session_list'),

    path(
        'sessions/<int:session_id>/start/',
        views.start_attendance,
        name='start_attendance'
    ),

    path(
        'sessions/<int:session_id>/take/',
        views.take_attendance,
        name='take_attendance'
    ),

    path(
        'sessions/<int:session_id>/recognize/',
        views.recognize_and_mark_attendance,
        name='recognize_and_mark_attendance'
    ),

    path(
        'report/<int:session_id>/',
        views.attendance_report,
        name='attendance_report'
    ),

]
