# Generated by Django 3.2.22 on 2024-10-04 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0012_contracttemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='contracttemplate',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_templates', to='medias.file'),
        ),
    ]