# Generated by Django 4.1.5 on 2023-01-28 18:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='allocation_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
