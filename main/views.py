from django.shortcuts import render

from main.forms import CustomUserCreationForm, CustomUserAuthForm


def registration_view(request):
    if request.method == "POST":
        reg_form = CustomUserCreationForm(request.POST)
        if reg_form.is_valid():
            reg_form.save()
    else:
        reg_form = CustomUserCreationForm()

    log_form = CustomUserAuthForm()

    return render(request, 'main/auth.html', {'reg_form': reg_form, 'log_form': log_form})
