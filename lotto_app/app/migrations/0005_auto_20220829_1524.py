# Generated by Django 3.1.8 on 2022-08-29 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_purchasedtickets_statenumbers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchasedtickets',
            old_name='game',
            new_name='game_obj',
        ),
        migrations.RenameField(
            model_name='statenumbers',
            old_name='game',
            new_name='game_obj',
        ),
    ]
