from django.urls import path
from main.views import *

urlpatterns = [
    path('auth/', registration_view, name='registration'),
]
