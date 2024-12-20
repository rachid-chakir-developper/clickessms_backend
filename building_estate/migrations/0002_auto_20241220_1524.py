# Generated by Django 3.2.22 on 2024-12-20 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0035_companymedia_blog_url'),
        ('medias', '0013_contracttemplate_image'),
        ('building_estate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spaceroom',
            name='establishment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='establishment_space_rooms', to='companies.establishment'),
        ),
        migrations.AddField(
            model_name='spaceroom',
            name='folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medias.folder'),
        ),
    ]
