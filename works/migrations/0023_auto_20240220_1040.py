# Generated by Django 3.2.22 on 2024-02-20 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0022_auto_20240218_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='billing_address',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='contractor_email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='contractor_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='contractor_tel',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='receiver_email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='receiver_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='receiver_tel',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='address',
            field=models.TextField(default='', null=True),
        ),
    ]
