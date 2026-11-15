
from django.shortcuts import render
from django.utils import timezone

from students.models import Student
from attendance.models import Attendance, AttendanceSession


def dashboard_home(request):

    today = timezone.localdate()

    # Total registered students
    total_students = Student.objects.count()

    # Get today's attendance sessions
    today_sessions = AttendanceSession.objects.filter(
        date=today
    ).select_related('class_obj')

    present_today = 0
    late_today = 0
    absent_today = 0
    total_attendance_slots = 0

    for session in today_sessions:

        # Get students belonging to this class
        class_students = Student.objects.filter(
            semester=session.class_obj.semester,
            section=session.class_obj.section
        )

        class_student_count = class_students.count()

        # Get attendance records for this session
        records = Attendance.objects.filter(
            session=session
        )

        present_today += records.filter(
            status='present'
        ).count()

        late_today += records.filter(
            status='late'
        ).count()

        explicitly_absent = records.filter(
            status='absent'
        ).count()

        marked_count = records.count()

        # Students without attendance records
        unmarked_count = max(
            0,
            class_student_count - marked_count
        )

        absent_today += explicitly_absent + unmarked_count

        total_attendance_slots += class_student_count

    # Calculate attendance percentage
    attended = present_today + late_today

    if total_attendance_slots > 0:
        attendance_rate = round(
            (attended / total_attendance_slots) * 100,
            2
        )
    else:
        attendance_rate = 0

    context = {
        'total_students': total_students,
        'present_today': present_today,
        'late_today': late_today,
        'absent_today': absent_today,
        'attendance_rate': attendance_rate,
    }

    return render(
        request,
        'dashboard/home.html',
        context
    )
