from typing import List

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from main.models import Subject, User, Question, Test, Schedule


class ICharField(forms.CharField):
    def __init__(self, *, image_url=None, text='', answer=None, source=None, **kwargs):
        super().__init__(**kwargs)
        self.image_url = image_url
        self.text = text
        self.answer = answer
        self.source = source


class TestForm(forms.Form):
    def __init__(self, test, questions: List[Question], **kwargs):
        super().__init__(**kwargs)
        self.test = test
        self.questions = questions
        self.result_source = 0

        i = 1
        for quest in questions:
            self.fields[str(quest.id)] = ICharField(label='Задание №%s' % i, text=quest.question_text,
                                                    image_url=quest.image.url if quest.image else None,
                                                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                    required=False, answer=quest.answer, source=quest.primary_score)
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


class TestCreationForm(forms.Form):
    name = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-control'}))
    theme = forms.CharField(label='Тема', widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), to_field_name='name',
                                     widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, data=None, **kwargs):
        super().__init__(data=data, **kwargs)

        if data:
            for field_name in data.keys():
                if field_name.startswith('question_text_'):
                    self.fields[field_name] = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
                elif field_name.startswith('image_'):
                    self.fields[field_name] = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}),
                                                              required=False)
                elif field_name.startswith('answer_'):
                    self.fields[field_name] = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
                elif field_name.startswith('source_'):
                    self.fields[field_name] = forms.IntegerField(
                        widget=forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}))

    def save(self):
        test = Test(name=self.cleaned_data['name'], theme=self.cleaned_data['theme'],
                    subject=Subject.objects.get(name=self.cleaned_data['subject']))
        test.save()

        for key, _ in self.fields.items():
            if key.startswith('question_text_'):
                num = key.replace('question_text_', '')

                question = self.cleaned_data[key]

                image_field_name = 'image_%s' % num
                if image_field_name in self.files.keys():
                    image = self.files.get(image_field_name)
                else:
                    image = None

                answer = self.cleaned_data['answer_%s' % num]
                source = self.cleaned_data['source_%s' % num]
                question = Question(test_id=test.id, question_text=question, image=image, answer=answer,
                                    primary_score=source)
                question.save()
                print(question)


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(),
                                              widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                                              required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar', 'subjects']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
