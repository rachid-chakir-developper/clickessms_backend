# Generated by Django 3.2.22 on 2025-01-13 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0064_beneficiaryadmission_status_reason'),
        ('feedbacks', '0018_comment_beneficiary_admission'),
        ('sales', '0019_auto_20250110_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='human_ressources.employee'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='managers',
            field=models.ManyToManyField(related_name='manager_invoices', to='human_ressources.Employee'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='signature',
            field=models.ManyToManyField(related_name='invoices', to='feedbacks.Signature'),
        ),
    ]