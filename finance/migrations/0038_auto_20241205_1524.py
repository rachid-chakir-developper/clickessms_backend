# Generated by Django 3.2.22 on 2024-12-05 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0013_contracttemplate_image'),
        ('finance', '0037_auto_20241205_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashregistertransaction',
            name='date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='cashregistertransaction',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transaction_document', to='medias.file'),
        ),
    ]
