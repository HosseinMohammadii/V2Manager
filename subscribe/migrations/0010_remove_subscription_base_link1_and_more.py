# Generated by Django 4.2 on 2023-05-10 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0009_server_port'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='base_link1',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='base_link2',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='base_link3',
        ),
    ]
