# Generated by Django 3.2.22 on 2024-11-25 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administratives', '0043_auto_20241121_1226'),
        ('works', '0038_auto_20241022_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskaction',
            name='meeting_decision',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions', to='administratives.meetingdecision'),
        ),
    ]
