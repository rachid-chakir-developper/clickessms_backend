# Generated by Django 3.2.22 on 2024-12-10 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0029_purchaseorder_expense'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorderitem',
            old_name='amount',
            new_name='amount_ttc',
        ),
    ]
