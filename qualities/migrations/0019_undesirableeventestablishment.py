# Generated by Django 3.2.22 on 2024-04-02 08:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0009_establishment_establishment_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qualities', '0018_auto_20240318_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='UndesirableEventEstablishment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='undesirable_event_establishment_former', to=settings.AUTH_USER_MODEL)),
                ('establishment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='undesirable_event_establishment', to='companies.establishment')),
                ('undesirable_event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='qualities.undesirableevent')),
            ],
        ),
    ]