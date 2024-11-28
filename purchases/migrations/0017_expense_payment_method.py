# Generated by Django 3.2.22 on 2024-11-28 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0016_expenseitem_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='payment_method',
            field=models.CharField(choices=[('CASH', 'Espèces'), ('CREDIT_CARD', 'Carte de crédit'), ('BANK_TRANSFER', 'Virement bancaire'), ('DIRECT_DEBIT', 'Prélèvement'), ('PAYPAL', 'PayPal'), ('CHECK', 'Chèque'), ('BILL_OF_EXCHANGE', 'Lettre de change relevé'), ('LIBEO_TRANSFER', 'Virement par Libeo'), ('MOBILE_PAYMENT', 'Paiement mobile'), ('CRYPTOCURRENCY', 'Cryptomonnaie'), ('DEBIT_CARD', 'Carte de débit'), ('APPLE_PAY', 'Apple Pay'), ('GOOGLE_PAY', 'Google Pay')], default='BANK_TRANSFER', max_length=50),
        ),
    ]
