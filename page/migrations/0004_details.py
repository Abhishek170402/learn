# Generated by Django 5.1.2 on 2024-11-02 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0003_studenthistory_delete_yourmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('student_class', models.CharField(max_length=10)),
                ('mark', models.IntegerField()),
            ],
        ),
    ]
