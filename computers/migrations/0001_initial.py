# Generated by Django 3.2.22 on 2024-12-12 09:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0033_auto_20241125_1105'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medias', '0013_contracttemplate_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(editable=False, max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('bar_code', models.CharField(max_length=255)),
                ('is_blocked', models.BooleanField(null=True)),
                ('is_stock_auto', models.BooleanField(null=True)),
                ('designation', models.TextField(default='', null=True)),
                ('buying_price_ht', models.FloatField(null=True)),
                ('tva', models.FloatField(null=True)),
                ('quantity', models.IntegerField(null=True)),
                ('description', models.TextField(default='', null=True)),
                ('observation', models.TextField(default='', null=True)),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('is_deleted', models.BooleanField(default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_softwares', to='companies.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('folder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder')),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='software_image', to='medias.file')),
            ],
        ),
    ]
