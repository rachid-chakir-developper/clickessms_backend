# Generated by Django 3.2.22 on 2024-05-15 10:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0018_establishment_establishment_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecisionDocumentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starting_date_time', models.DateTimeField(null=True)),
                ('ending_date_time', models.DateTimeField(null=True)),
                ('price', models.FloatField(null=True)),
                ('endowment', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decision_document_item_former', to=settings.AUTH_USER_MODEL)),
                ('decision_document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.decisiondocument')),
                ('establishment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_decision_document_items', to='companies.establishment')),
            ],
        ),
    ]
