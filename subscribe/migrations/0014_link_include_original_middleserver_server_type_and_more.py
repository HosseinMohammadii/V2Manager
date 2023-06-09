# Generated by Django 4.2 on 2023-05-19 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0013_subscription_last_check_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='include_original',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='middleserver',
            name='server_type',
            field=models.CharField(choices=[('Arvan', 'Arvan'), ('Cloudflare', 'Cloudflare'), ('Fragment', 'Fragment')], default='Fragment', max_length=32),
        ),
        migrations.AddField(
            model_name='server',
            name='middle_servers',
            field=models.ManyToManyField(to='subscribe.middleserver'),
        ),
    ]
