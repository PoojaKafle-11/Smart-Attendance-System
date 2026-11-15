
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone

from academics.models import Class
from students.models import Student

from .models import AttendanceSession, Attendance

from ai_service.recognition_service import recognize_face


# =========================================
# 1. CREATE ATTENDANCE SESSION
# =========================================

@login_required(login_url='teacher_login')


def create_session(request):

    teacher = request.user.teacher_profile

    classes = Class.objects.filter(teacher=teacher)

    if request.method == 'POST':

        class_id = request.POST.get('class_id')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        grace_period = request.POST.get('grace_period', '10')

        selected_class = classes.filter(id=class_id).first()

        if not selected_class:
            messages.error(request, 'Invalid class selected.')
            return redirect('create_session')

        if not date or not start_time or not end_time:
            messages.error(request, 'Please fill in all fields.')
            return redirect('create_session')

        if end_time <= start_time:
            messages.error(
                request,
                'End time must be later than start time.'
            )
            return redirect('create_session')

        if grace_period not in ['0', '5', '10', '15', '20', '30']:
            messages.error(request, 'Invalid grace period.')
            return redirect('create_session')

        AttendanceSession.objects.create(
            class_obj=selected_class,
            date=date,
            start_time=start_time,
            end_time=end_time,
            grace_period=int(grace_period),
            status='scheduled'
        )

        messages.success(
            request,
            'Attendance session created successfully!'
        )

        return redirect('create_session')

    return render(
        request,
        'attendance/create_session.html',
        {'classes': classes}
    )

# =========================================
# 2. SESSION LIST
# =========================================

@login_required(login_url='teacher_login')
def session_list(request):

    teacher = request.user.teacher_profile

    sessions = AttendanceSession.objects.filter(
        class_obj__teacher=teacher
    ).order_by('-date', '-start_time')
    for session in sessions:
        update_session_status(session)
    return render(
        request,
        'attendance/session_list.html',
        {'sessions': sessions}
    )

# =========================================
# ATTENDANCE REPORT
# =========================================

@login_required(login_url='teacher_login')
def attendance_report(request, session_id):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        class_obj__teacher=teacher
    )

    # Get all students belonging to this class
    students = Student.objects.filter(
        semester=session.class_obj.semester,
        section=session.class_obj.section
    ).order_by('name')

    # Get attendance records for this session
    attendance_records = Attendance.objects.filter(
        session=session
    ).select_related('student')

    # Create a lookup dictionary
    attendance_dict = {
        record.student_id: record
        for record in attendance_records
    }

    report = []

    for student in students:

        attendance = attendance_dict.get(student.id)

        if attendance:
            status = attendance.status
            marked_at = attendance.marked_at
            confidence = attendance.confidence
        else:
            status = 'absent'
            marked_at = None
            confidence = None

        report.append({
            'student': student,
            'status': status,
            'marked_at': marked_at,
            'confidence': confidence
        })

    # Calculate attendance summary
    total_students = len(report)

    present_count = sum(
        1 for item in report
        if item['status'] == 'present'
    )

    late_count = sum(
        1 for item in report
        if item['status'] == 'late'
    )

    absent_count = sum(
        1 for item in report
        if item['status'] == 'absent'
    )

    attendance_rate = (
        round(((present_count + late_count) / total_students) * 100, 2)
        if total_students > 0 else 0
    )

    return render(
        request,
        'attendance/attendance_report.html',
        {
            'session': session,
            'report': report,
            'total_students': total_students,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'attendance_rate': attendance_rate,
        }
    )



# =========================================
# 3. START ATTENDANCE SESSION
# =========================================

@login_required(login_url='teacher_login')
@require_POST
def start_attendance(request, session_id):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        class_obj__teacher=teacher
    )

    if session.status == 'scheduled':

        session.status = 'active'

        session.save(update_fields=['status'])

    return redirect('session_list')


# =========================================
# 4. TAKE ATTENDANCE PAGE
# =========================================

@login_required(login_url='teacher_login')
def take_attendance(request, session_id):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        class_obj__teacher=teacher
    )
    update_session_status(session)
    if session.status != 'active':
        return redirect('session_list')

    return render(
        request,
        'attendance/take_attendance.html',
        {'session': session}
    )


# =========================================
# 5. RECOGNIZE FACE AND MARK ATTENDANCE
# =========================================

@login_required(login_url='teacher_login')
@require_POST
def recognize_and_mark_attendance(request, session_id):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        class_obj__teacher=teacher
    )
    update_session_status(session)
    if session.status != 'active':

        return JsonResponse({
            'success': False,
            'message': 'Attendance session is not active.'
        }, status=400)

    image = request.FILES.get('image')

    if not image:

        return JsonResponse({
            'success': False,
            'message': 'No camera image received.'
        }, status=400)

    try:

        # Recognize face using InsightFace
        result = recognize_face(image.read())

        if not result['recognized']:

            return JsonResponse({
                'success': False,
                'message': result.get(
                    'message',
                    'Face not recognized.'
                )
            })

        # Find student in database
        # student = Student.objects.filter(
        #     student_id=result['student_id']
        # ).first()
        # replaceable
        print("Recognized ID:", result['student_id'])

        print("All student IDs:", list(
            Student.objects.values_list('student_id', flat=True)
        ))

        student = Student.objects.filter(
            student_id=result['student_id']
        ).first()

        print("Database student found:", student)

        if not student:

            return JsonResponse({
                'success': False,
                'message': 'Student not found.'
            })
        print("Student semester:", student.semester)
        print("Class semester:", session.class_obj.semester)

        print("Student section:", student.section)
        print("Class section:", session.class_obj.section)
        # Verify student belongs to this class
        if (
            student.semester != session.class_obj.semester
            or student.section != session.class_obj.section
        ):

            return JsonResponse({
                'success': False,
                'message': 'Student does not belong to this class.'
            })

        # Get current local time
        current_time = timezone.localtime()

        # Combine session date and start time
        session_start = timezone.make_aware(
            datetime.combine(session.date, session.start_time)
        )

        # Combine session date and end time
        session_end = timezone.make_aware(
            datetime.combine(session.date, session.end_time)
        )

        # Calculate grace period deadline
        grace_deadline = session_start + timedelta(
            minutes=session.grace_period
        )

        # Prevent attendance before session starts
        if current_time < session_start:

            return JsonResponse({
                'success': False,
                'message': 'Attendance has not started yet.'
            })

        # Prevent attendance after session ends
        if current_time > session_end:

            return JsonResponse({
                'success': False,
                'message': 'Attendance session has ended.'
            })

        # Determine attendance status
        if current_time <= grace_deadline:
            attendance_status = 'present'
        else:
            attendance_status = 'late'

        # Save attendance without creating duplicates
        attendance, created = Attendance.objects.get_or_create(
            session=session,
            student=student,
            defaults={
                'status': attendance_status,
                'confidence': result['similarity']
            }
        )

        return JsonResponse({
            'success': True,
            'created': created,
            'student_name': student.name,
            'student_id': student.student_id,
            'status': attendance.get_status_display(),
            'similarity': result['similarity'],
            'message': (
                'Attendance marked successfully.'
                if created
                else 'Attendance already marked.'
            )
        })

    except Exception as e:

        print('Recognition error:', e)

        return JsonResponse({
            'success': False,
            'message': 'Face recognition failed.'
        }, status=500)


def update_session_status(session):

    if session.status == 'completed':
        return session

    session_end = timezone.make_aware(
        datetime.combine(session.date, session.end_time),
        timezone.get_current_timezone()
    )

    if timezone.now() >= session_end:

        session.status = 'completed'

        session.save(update_fields=['status'])

    return session
