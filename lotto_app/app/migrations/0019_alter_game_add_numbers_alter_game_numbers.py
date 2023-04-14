# Generated by Django 4.0.1 on 2023-04-14 10:26

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_rename_no_numbers_a_game_no_numbers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='add_numbers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(89)]), blank=True, null=True, size=89),
        ),
        migrations.AlterField(
            model_name='game',
            name='numbers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(90)]), size=90),
        ),
    ]
