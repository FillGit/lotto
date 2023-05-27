# Generated by Django 4.0.1 on 2023-05-12 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_remove_statenumbers_not unique game and number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statenumbers',
            name='state',
        ),
        migrations.AddField(
            model_name='statenumbers',
            name='amount_used',
            field=models.IntegerField(default=0),
        ),
    ]