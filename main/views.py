from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from main.decorators import anonymous_required, test_not_finished_required
from main.forms import UserRegistrationForm, UserLoginForm, TestForm
from main.models import Question, Test, Subject, TestHistory, CourseVideo
from main.services import save_user_test


@login_required
@test_not_finished_required
def test_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = Question.objects.filter(test_id=test.id)

    if request.method == 'POST':
        form = TestForm(test, questions, data=request.POST)
        if form.is_valid():
            save_user_test(request.user, form)
            return redirect('home')
    else:
        form = TestForm(test, questions)

    return render(request, 'main/test.html', {'form': form})


@anonymous_required
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, email=form.cleaned_data['email'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('home')
            else:
                form.errors['email'] = 'Неверное имя пользователя или пароль'
    else:
        form = UserLoginForm()

    return render(request, 'main/login.html', {'form': form})


@anonymous_required
def registration_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = UserRegistrationForm()

    return render(request, 'main/registration.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home_view(request):

    return render(request, 'main/homeworks.html')


@login_required
def homework_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    tests_all = Test.objects.filter(subject_id=subject.id)

    tests_done = TestHistory.objects.filter(test__subject_id=subject.id, user_id=request.user.id)

    tests = []
    passed_tests_id = [x['test_id'] for x in tests_done.values('test_id')]
    for test in tests_all:
        if test.id not in passed_tests_id:
            tests.append(test)

    return render(request, 'main/homeworks.html', {'page_subject': subject, 'tests_done': tests_done, 'tests': tests})


def course_view(request, course_id):
    subject = get_object_or_404(Subject, id=course_id)
    videos = CourseVideo.objects.filter(subject_id=subject.id)

    return render(request, 'main/courses.html', {'page_subject': subject, 'videos': videos})


def schedule_view(request):
    return render(request, 'main/schedule.html')

