from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from main.decorators import *
from main.forms import UserRegistrationForm, UserLoginForm, TestForm, TestCreationForm, ScheduleForm, ProfileUpdateForm
from main.models import Question, Test, Subject, TestHistory, CourseVideo, Schedule, User
from main.services import save_user_test, get_test_questions_sources, get_pagination_vars, get_subject_of_page_and_all
from main.utils import get_video_title, get_video_id


@login_required
@teacher_required
def teacher_video_view(request, subject_id):
    if request.method == 'POST':
        if 'new_video' in request.POST.keys():
            video_id = get_video_id(request.POST['new_video'])
            title = get_video_title(video_id)
            video = CourseVideo(url='https://www.youtube.com/embed/%s' % video_id, title=title, subject_id=subject_id)
            video.save()
        else:
            video = CourseVideo.objects.get(id=request.POST['video_id'])
            video.delete()

        return redirect('teacher_video', subject_id)

    context = get_subject_of_page_and_all(subject_id)

    videos = CourseVideo.objects.filter(subject=context['subject_page'])
    context['videos'] = videos

    context.update(get_pagination_vars(request, videos))

    return render(request, 'main/teacher_videos_page.html', context=context)


@login_required
@teacher_required
def teacher_test_creation_view(request):
    if request.method == 'POST':
        form = TestCreationForm(request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            subject_id = Subject.objects.get(name=form.cleaned_data['subject']).id
            return redirect('teacher_hw', subject_id)
    else:
        form = TestCreationForm()
    return render(request, 'main/teacher_test_creation.html', {'form': form})


@login_required
@teacher_required
def teacher_hw_view(request, subject_id):
    if request.method == 'POST':
        test = get_object_or_404(Test, id=request.POST['test_id'])
        test.delete()

        return redirect('teacher_hw', subject_id)

    context = get_subject_of_page_and_all(subject_id)
    tests = Test.objects.filter(subject=context['subject_page'])

    tests_source = {}

    for test in tests:
        tests_source[test] = get_test_questions_sources(test)

    context['tests_source'] = tests_source
    context.update(get_pagination_vars(request, tests))

    return render(request, 'main/teacher_hw.html', context=context)


@login_required
@test_not_finished_required
def test_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = Question.objects.filter(test_id=test.id)

    if request.method == 'POST':
        form = TestForm(test, questions, data=request.POST)
        if form.is_valid():
            save_user_test(request.user, form)
            return render(request, 'main/test_results.html', {'form': form})
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
                return redirect('profile')
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
            return redirect('profile')

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


@login_required
def course_view(request, course_id):
    subject = get_object_or_404(Subject, id=course_id)
    search = request.GET.get('name', '')
    if search:
        videos = CourseVideo.objects.filter(title__icontains=search, subject_id=subject.id)
    else:
        videos = CourseVideo.objects.filter(subject_id=subject.id)

    return render(request, 'main/courses.html', {'page_subject': subject, 'videos': videos})


@login_required
def schedule_view(request):
    if request.method == 'POST':
        if User.objects.get(id=request.user.id).role == Role.teacher:
            form = ScheduleForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('schedule')

    form = ScheduleForm()
    schedule = Schedule.objects.first()
    return render(request, 'main/schedule.html', {'form': form, 'schedule': schedule})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'main/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return User.objects.get(id=self.request.user.id)
