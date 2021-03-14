from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum, Max, F
from django.urls import reverse


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

    def get_url_on_homework(self):
        return reverse('homework', kwargs={'subject_id': self.id})

    def get_url_on_course(self):
        return reverse('course', kwargs={'course_id': self.id})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('email должен быть указан')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True, verbose_name='Email')
    username = models.CharField(max_length=30, blank=False, verbose_name='Имя')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Время регистрации')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    avatar = models.ImageField(upload_to='avatars/', default=settings.DEFAULT_USER_AVATAR,
                               null=True, blank=True, verbose_name='Аватар')
    coins = models.PositiveIntegerField(default=0, null=False, verbose_name='Коины')
    subjects = models.ManyToManyField(Subject, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class CourseVideo(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Предмет')
    url = models.URLField(verbose_name='Ссылка на видео')


class Test(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Предмет')
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Название теста')
    theme = models.CharField(max_length=100, blank=False, null=False, verbose_name='Тема')

    def get_absolute_url(self):
        return reverse('test', kwargs={'test_id': self.id})

    def get_test_source(self):
        return self.question_set.aggregate(Sum(F('primary_score')))['primary_score__sum']


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Тест')
    image = models.ImageField(upload_to='question/', null=True, blank=True, verbose_name='Изображение вопроса')
    question_text = models.TextField(max_length=1000, blank=False, null=False, verbose_name='Содержание вопроса')
    answer = models.CharField(max_length=50, blank=False, null=False, verbose_name='Ответ')
    primary_score = models.PositiveIntegerField(blank=False, null=False, verbose_name='Первичный балл')


class TestHistory(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Тест')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, verbose_name='Пользователь')
    primary_source = models.PositiveIntegerField(blank=False, default=0, verbose_name='Набранный балл')


class AnswerHistory(models.Model):
    test_history = models.ForeignKey(TestHistory, on_delete=models.CASCADE, blank=False, null=False,
                                     verbose_name='Тест')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Вопрос')
    user_answer = models.CharField(max_length=50, blank=False, null=False, verbose_name='Ответ')
    is_correct = models.BooleanField(blank=False, null=False, verbose_name='Ответ верный?')
