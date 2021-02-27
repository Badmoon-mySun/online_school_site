from django import forms
from django.core.exceptions import ValidationError

from main.models import Subject, User


class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Ваше имя', widget=forms.TextInput(attrs={'class': 'form-control'}),
                               min_length=1, max_length=15)
    email = forms.CharField(label='Ваш Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(),
                                              widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                                              required=True)

    def get_required_fields(self):
        return [self.username, self.email, self.password]

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if User.objects.filter(email=email).count():
            raise ValidationError('Email already exists')

        return email

    def save(self):

        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            username=self.cleaned_data['username'],
        )

        user.subjects.add(*self.cleaned_data['subjects'])

        user.save()

        return user


class CustomUserAuthForm(forms.Form):
    email = forms.CharField(label='Ваш Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
