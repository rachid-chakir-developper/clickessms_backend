# Generated by Django 3.2.22 on 2025-02-27 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('human_ressources', '0081_alter_beneficiaryentry_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='beneficiaryadmissiondocument',
            options={'ordering': ['starting_date']},
        ),
        migrations.AlterModelOptions(
            name='beneficiaryendowmententry',
            options={'ordering': ['starting_date']},
        ),
        migrations.AlterModelOptions(
            name='beneficiarystatusentry',
            options={'ordering': ['starting_date']},
        ),
        migrations.AlterModelOptions(
            name='careerentry',
            options={'ordering': ['starting_date']},
        ),
    ]
