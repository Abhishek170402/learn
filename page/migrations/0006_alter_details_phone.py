# Generated by Django 5.1.2 on 2024-11-02 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0005_details_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='details',
            name='phone',
            field=models.CharField(max_length=15),
        ),
    ]
