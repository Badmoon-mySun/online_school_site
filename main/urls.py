from django.urls import path
from main.views import *

urlpatterns = [
    path('', ProfileUpdateView.as_view(), name='profile'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registration/', registration_view, name='registration'),
    path('homework/subject-<str:subject_id>/', homework_view, name='homework'),
    path('course/subject-<str:course_id>/', course_view, name='course'),
    path('schedule/', schedule_view, name='schedule'),
    path('test/<str:test_id>/', test_view, name='test'),
    path('teacher/subject-<str:subject_id>/', teacher_hw_view, name='teacher_hw'),
    path('teacher/test/create/', teacher_test_creation_view, name='teacher_test_creation'),
    path('teacher/video/subject-<str:subject_id>/', teacher_video_view, name='teacher_video')
]
