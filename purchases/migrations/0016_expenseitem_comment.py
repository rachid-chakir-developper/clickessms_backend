# Generated by Django 3.2.22 on 2024-11-28 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0015_expense_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenseitem',
            name='comment',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]