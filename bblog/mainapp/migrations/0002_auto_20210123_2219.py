# Generated by Django 3.1.5 on 2021-01-23 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pageviews',
            field=models.IntegerField(default=0, verbose_name='文章浏览量'),
        ),
    ]