# Generated by Django 3.1.7 on 2021-03-21 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210319_1422'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default=None, upload_to='schedules/', verbose_name='Изображение с расписанием')),
                ('upload_date', models.DateTimeField(auto_now=True, verbose_name='Время загрузки')),
            ],
            options={
                'verbose_name': 'Расписания',
                'verbose_name_plural': 'Расписание',
                'ordering': ['-upload_date'],
            },
        ),
        migrations.AlterModelOptions(
            name='coursevideo',
            options={'ordering': ['-id'], 'verbose_name': 'Видео', 'verbose_name_plural': 'Видео'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Вопросы', 'verbose_name_plural': 'Вопрос'},
        ),
        migrations.AlterModelOptions(
            name='test',
            options={'verbose_name': 'Тест', 'verbose_name_plural': 'Тесты'},
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
    ]
