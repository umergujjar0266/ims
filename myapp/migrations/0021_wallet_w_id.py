# Generated by Django 5.0.6 on 2024-06-14 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_remove_wallet_balance_alter_wallet_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='w_id',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
    ]
