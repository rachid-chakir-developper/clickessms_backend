# Generated by Django 3.2.22 on 2024-06-07 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0038_auto_20240530_1526'),
        ('qualities', '0028_auto_20240607_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='undesirableeventreview',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='undesirable_event_reviews', to='human_ressources.employee'),
        ),
        migrations.AlterField(
            model_name='undesirableeventaction',
            name='undesirable_event_review',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions', to='qualities.undesirableeventreview'),
        ),
        migrations.AlterField(
            model_name='undesirableeventreview',
            name='undesirable_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to='qualities.undesirableevent'),
        ),
    ]
