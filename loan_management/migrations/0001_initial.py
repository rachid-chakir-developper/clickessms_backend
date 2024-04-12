# Generated by Django 3.2.22 on 2024-01-03 10:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sales', '0001_initial'),
        ('medias', '0008_alter_folder_folder'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TheObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='the_object_image', to='medias.file')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectRecovery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('recovery_date', models.DateTimeField(null=True)),
                ('return_date', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='the_object_client', to='sales.client')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('images', models.ManyToManyField(related_name='object_recovery_images', to='medias.File')),
                ('the_object', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='the_object_recovery', to='loan_management.theobject')),
                ('videos', models.ManyToManyField(related_name='object_recovery_videos', to='medias.File')),
            ],
        ),
    ]