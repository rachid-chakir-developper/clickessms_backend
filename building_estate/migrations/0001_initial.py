# Generated by Django 3.2.22 on 2024-12-20 11:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('medias', '0013_contracttemplate_image'),
        ('companies', '0035_companymedia_blog_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpaceRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('room_type', models.CharField(choices=[('MEETING', 'Salle de réunion'), ('CONFERENCE', 'Salle de conférence'), ('LOUNGE', 'Salle de pause'), ('TRAINING', 'Salle de formation'), ('PHONE', 'Cabine téléphonique'), ('OFFICE', 'Bureau privé'), ('STUDIO', 'Studio'), ('OTHER', 'Autre')], default='MEETING', max_length=20)),
                ('capacity', models.PositiveIntegerField(null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_space_rooms', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='space_rooms_former', to=settings.AUTH_USER_MODEL)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='space_rooms', to='medias.file')),
            ],
        ),
    ]
