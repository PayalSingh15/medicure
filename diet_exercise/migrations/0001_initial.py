# Generated by Django 5.1.5 on 2025-02-07 19:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExerciseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='VitaminDeficiency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('recommended_foods', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ExercisePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('bmi_category', models.CharField(max_length=20)),
                ('goal', models.CharField(max_length=20)),
                ('exercises', models.JSONField(default=dict)),
                ('total_duration', models.IntegerField(default=30)),
                ('categories', models.ManyToManyField(to='diet_exercise.exercisecategory')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserHealthProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('gender', models.CharField(max_length=20)),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
                ('activity_level', models.CharField(max_length=20)),
                ('goal', models.CharField(default='maintenance', max_length=20)),
                ('medical_conditions', models.TextField(blank=True)),
                ('dietary_restrictions', models.TextField(blank=True)),
                ('preferred_exercise_categories', models.ManyToManyField(blank=True, to='diet_exercise.exercisecategory')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vitamin_deficiencies', models.ManyToManyField(blank=True, to='diet_exercise.vitamindeficiency')),
            ],
        ),
        migrations.CreateModel(
            name='DietPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('bmi_category', models.CharField(max_length=20)),
                ('goal', models.CharField(max_length=20)),
                ('daily_calories', models.IntegerField(default=2000)),
                ('breakfast', models.JSONField(default=list)),
                ('lunch', models.JSONField(default=list)),
                ('dinner', models.JSONField(default=list)),
                ('snacks', models.JSONField(default=list)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vitamin_deficiencies', models.ManyToManyField(blank=True, to='diet_exercise.vitamindeficiency')),
            ],
        ),
    ]
