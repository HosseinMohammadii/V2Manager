# Generated by Django 5.0 on 2024-07-18 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0020_server_end_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='operating',
            field=models.BooleanField(default=True),
        ),
    ]
