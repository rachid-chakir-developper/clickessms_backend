# Generated by Django 3.2.22 on 2024-11-21 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0013_contracttemplate_image'),
        ('companies', '0030_alter_company_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='collective_agreement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='collective_agreement_companies', to='medias.file'),
        ),
        migrations.AddField(
            model_name='company',
            name='company_agreement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_agreement_companies', to='medias.file'),
        ),
    ]
