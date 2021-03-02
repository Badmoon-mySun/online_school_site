from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from main.decorators import anonymous_required
from main.forms import UserRegistrationForm, UserLoginForm


@anonymous_required
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['email'],
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
    pass
