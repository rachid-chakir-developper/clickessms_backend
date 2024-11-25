# Generated by Django 3.2.22 on 2024-11-25 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0013_contracttemplate_image'),
        ('companies', '0032_auto_20241121_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='companymedia',
            name='associations_foundations_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='associations_foundations_code_company_medias', to='medias.file'),
        ),
        migrations.AddField(
            model_name='companymedia',
            name='labor_law',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='labor_law_company_medias', to='medias.file'),
        ),
        migrations.AddField(
            model_name='companymedia',
            name='safc_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='safc_code_company_medias', to='medias.file'),
        ),
    ]
