# Generated by Django 3.1.5 on 2021-03-09 12:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_text_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='create_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='创建时间'),
        ),
    ]
