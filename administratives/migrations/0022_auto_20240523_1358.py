# Generated by Django 3.2.22 on 2024-05-23 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administratives', '0021_meeting_meeting_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingDecision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.TextField(default='', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meeting_decision_former', to=settings.AUTH_USER_MODEL)),
                ('meeting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administratives.meeting')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingReviewPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_to_review', models.TextField(default='', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='review_point_former', to=settings.AUTH_USER_MODEL)),
                ('meeting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administratives.meeting')),
            ],
        ),
        migrations.RemoveField(
            model_name='meetingreportitem',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='meetingreportitem',
            name='meeting_report',
        ),
        migrations.DeleteModel(
            name='MeetingReport',
        ),
        migrations.DeleteModel(
            name='MeetingReportItem',
        ),
    ]
