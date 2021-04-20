# Generated by Django 3.1.7 on 2021-04-20 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursevideo',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='questions/', verbose_name='Изображение вопроса'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар'),
        ),
    ]
