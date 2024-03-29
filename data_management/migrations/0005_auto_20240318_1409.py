# Generated by Django 3.2.22 on 2024-03-18 13:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_management', '0004_auto_20240315_1234'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UndesirableEventType',
            new_name='UndesirableEventNormalType',
        ),
        migrations.CreateModel(
            name='UndesirableEventSeriousType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('descreption', models.TextField(default='', null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
