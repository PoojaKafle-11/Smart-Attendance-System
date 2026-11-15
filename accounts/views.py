
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def teacher_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Check whether this user has a teacher profile
            if hasattr(user, 'teacher_profile'):
                login(request, user)
                return redirect('/dashboard/')

            messages.error(
                request,
                'You are not registered as a teacher.'
            )

        else:
            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(request, 'accounts/login.html')


def teacher_logout(request):

    if request.method == 'POST':
        logout(request)

    return redirect('teacher_login')
