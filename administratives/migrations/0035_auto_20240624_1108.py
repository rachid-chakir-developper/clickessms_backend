# Generated by Django 3.2.22 on 2024-06-24 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administratives', '0034_callemployee_callestablishment_letteremployee_letterestablishment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbeneficiary',
            name='call',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiaries', to='administratives.call'),
        ),
        migrations.AlterField(
            model_name='caller',
            name='call',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='callers', to='administratives.call'),
        ),
        migrations.AlterField(
            model_name='letterbeneficiary',
            name='letter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beneficiaries', to='administratives.letter'),
        ),
    ]
