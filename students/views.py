from django.shortcuts import render, redirect, get_object_or_404
from .models import Student


def student_list(request):

    students = Student.objects.all().order_by('-created_at')

    search = request.GET.get('search', '')
    semester = request.GET.get('semester', '')

    if search:
        students = students.filter(
            name__icontains=search
        ) | students.filter(
            student_id__icontains=search
        )

    if semester:
        students = students.filter(
            semester=semester
        )

    return render(
        request,
        'students/student_list.html',
        {
            'students': students,
            'search': search,
            'selected_semester': semester,
        }
    )


def add_student(request):

    if request.method == 'POST':

        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        semester = request.POST.get('semester')
        section = request.POST.get('section')
        profile_photo = request.FILES.get('profile_photo')

        Student.objects.create(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            semester=semester,
            section=section,
            profile_photo=profile_photo
        )

        return redirect('students:student_list')

    return render(
        request,
        'students/add_student.html'
    )


def edit_student(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if request.method == 'POST':

        student.student_id = request.POST.get('student_id')
        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        student.semester = request.POST.get('semester')
        student.section = request.POST.get('section')

        if request.FILES.get('profile_photo'):
            student.profile_photo = request.FILES.get(
                'profile_photo'
            )

        student.save()

        return redirect(
            'students:student_list'
        )

    return render(
        request,
        'students/edit_student.html',
        {
            'student': student
        }
    )


def delete_student(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if request.method == 'POST':
        student.delete()

    return redirect(
        'students:student_list'
    )