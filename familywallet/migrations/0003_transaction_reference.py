# Generated by Django 5.2 on 2025-07-12 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('familywallet', '0002_alter_transaction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='reference',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
