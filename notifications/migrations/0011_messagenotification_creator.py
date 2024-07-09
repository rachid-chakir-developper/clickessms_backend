# Generated by Django 3.2.22 on 2024-06-29 13:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0010_auto_20240629_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagenotification',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]