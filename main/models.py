from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager as DjangoUserManager
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum, F, Count
from django.urls import reverse
from djchoices import ChoiceItem, DjangoChoices


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')

    def get_url_on_homework(self):
        return reverse('homework', kwargs={'subject_id': self.id})

    def get_url_on_course(self):
        return reverse('course', kwargs={'course_id': self.id})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class CustomUserManager(DjangoUserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Role(DjangoChoices):
    admin = ChoiceItem()
    student = ChoiceItem()
    teacher = ChoiceItem()


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True, verbose_name='Email')
    username = models.CharField(max_length=30, blank=False, verbose_name='Имя')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Время регистрации')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    coins = models.PositiveIntegerField(default=0, null=False, verbose_name='Коины')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    role = models.CharField(choices=Role.choices, default=Role.student, max_length=50)
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
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name='Название')

    class Meta:
        verbose_name_plural = 'Видео'
        verbose_name = 'Видео'
        ordering = ['-id']


class Test(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Предмет')
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Название теста')
    theme = models.CharField(max_length=100, blank=False, null=False, verbose_name='Тема')

    def get_count_passes_user(self):
        return TestHistory.objects.filter(test_id=self.id).aggregate(count=Count('id'))['count']

    def get_absolute_url(self):
        return reverse('test', kwargs={'test_id': self.id})

    def get_test_source(self):
        return self.question_set.aggregate(Sum(F('primary_score')))['primary_score__sum']

    class Meta:
        verbose_name_plural = 'Тесты'
        verbose_name = 'Тест'


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Тест')
    image = models.ImageField(upload_to='questions/', null=True, blank=True, verbose_name='Изображение вопроса')
    question_text = models.TextField(max_length=1000, blank=False, null=False, verbose_name='Содержание вопроса')
    answer = models.CharField(max_length=50, blank=False, null=False, verbose_name='Ответ')
    primary_score = models.PositiveIntegerField(blank=False, null=False, verbose_name='Первичный балл')

    class Meta:
        verbose_name_plural = 'Вопрос'
        verbose_name = 'Вопросы'


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

    @staticmethod
    def get_count_correct_answers_for_question(question: Question):
        return AnswerHistory.objects.filter(question=question).filter(is_correct=True).aggregate(count=Count('id'))[
            'count']


class Schedule(models.Model):
    image = models.ImageField(default=None, upload_to='schedules/', verbose_name='Изображение с расписанием')
    upload_date = models.DateTimeField(auto_now=True, verbose_name='Время загрузки')

    class Meta:
        verbose_name_plural = 'Расписание'
        verbose_name = 'Расписания'
        ordering = ['-upload_date']
