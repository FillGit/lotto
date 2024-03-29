# Generated by Django 4.0.1 on 2023-05-12 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_remove_statenumbers_state_statenumbers_amount_used'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='statenumbers',
            name='not unique name_game and game_id',
        ),
        migrations.AddConstraint(
            model_name='statenumbers',
            constraint=models.UniqueConstraint(fields=('name_game', 'game_id', 'number'),
                                               name='not unique name_game and game_id and number'),
        ),
    ]
