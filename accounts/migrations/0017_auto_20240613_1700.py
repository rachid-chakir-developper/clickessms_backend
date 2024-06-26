# Generated by Django 3.2.22 on 2024-06-13 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partnerships', '0008_auto_20240520_1043'),
        ('purchases', '0008_supplier_company'),
        ('accounts', '0016_auto_20240610_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='financier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financier_user', to='partnerships.financier'),
        ),
        migrations.AddField(
            model_name='user',
            name='supplier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supplier_user', to='purchases.supplier'),
        ),
        migrations.AddField(
            model_name='usercompany',
            name='financier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='partnerships.financier'),
        ),
        migrations.AddField(
            model_name='usercompany',
            name='supplier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchases.supplier'),
        ),
    ]
