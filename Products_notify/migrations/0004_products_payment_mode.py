# Generated by Django 3.2 on 2022-09-16 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products_notify', '0003_alter_subscribe_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='payment_mode',
            field=models.CharField(default='Agreement', max_length=50),
        ),
    ]
