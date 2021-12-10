# Generated by Django 3.2.7 on 2021-12-07 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-datePosted']},
        ),
        migrations.AlterModelOptions(
            name='watchlist',
            options={'ordering': ['item']},
        ),
        migrations.RemoveField(
            model_name='itemtosell',
            name='onFire',
        ),
        migrations.AddField(
            model_name='listing',
            name='onFire',
            field=models.BooleanField(default=False),
        ),
    ]
