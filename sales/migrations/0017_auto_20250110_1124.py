# Generated by Django 3.2.22 on 2025-01-10 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0035_companymedia_blog_url'),
        ('sales', '0016_invoiceitem_measurement_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='establishment',
        ),
        migrations.AddField(
            model_name='invoice',
            name='establishments',
            field=models.ManyToManyField(related_name='invoices', to='companies.Establishment'),
        ),
    ]