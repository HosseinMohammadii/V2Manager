# Generated by Django 4.2 on 2023-05-19 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0011_server_panel_add_server_password_server_username_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FastSubscription',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('subscribe.subscription',),
        ),
        migrations.AddField(
            model_name='subscription',
            name='last_used_traffic',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='link',
            name='type',
            field=models.CharField(choices=[('URI', 'URI'), ('Subscription_Link', 'Subscription_Link'), ('Encoded', 'Encoded'), ('Clash', 'Clash'), ('URI_List', 'URI_List'), ('By Config ID', 'By Config ID')], default='By Config ID', max_length=64),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='expire_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
