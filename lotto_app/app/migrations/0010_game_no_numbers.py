# Generated by Django 4.0.1 on 2023-02-21 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_game_last_win_number_card_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='no_numbers',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
