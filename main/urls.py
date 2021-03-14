from django.urls import path
from main.views import *

urlpatterns = [
    path('registration/', registration_view, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
    path('homework/subject-<str:subject_id>/', homework_view, name='homework'),
    path('course/subject-<str:course_id>/', course_view, name='course'),
    path('schedule/', schedule_view, name='schedule'),
    path('test/<str:test_id>/', test_view, name='test'),
]
