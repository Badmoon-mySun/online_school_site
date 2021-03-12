from typing import List

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from main.models import Subject, User, Question, TestHistory, AnswerHistory


class ICharField(forms.CharField):
    def __init__(self, *, image_url=None, text='', **kwargs):
        super().__init__(**kwargs)
        self.image_url = image_url
        self.text = text


class TestForm(forms.Form):
    def __init__(self, test, questions: List[Question], **kwargs):
        super().__init__(**kwargs)
        self.test = test
        self.questions = questions

        i = 1
        for quest in questions:
            self.fields[str(quest.id)] = ICharField(label='Задание №%s' % i, text=quest.question_text,
                                                    image_url=quest.image.url if quest.image else None,
                                                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                    required=False)
            i += 1


class UserRegistrationForm(forms.Form):
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
            raise ValidationError('Пользователь с таким email уже существует')

        return email

    def clean_password(self):
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data['password']

    def save(self):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
        )

        user.subjects.add(*self.cleaned_data['subjects'])

        user.save()

        return user


class UserLoginForm(forms.Form):
    email = forms.CharField(label='Ваш Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
