# Generated by Django 4.0.1 on 2023-03-04 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20230227_1536'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lottotickets',
            old_name='ticket_number',
            new_name='ticket_id',
        ),
        migrations.RenameField(
            model_name='lottotickets',
            old_name='ticket_all_numbers',
            new_name='ticket_numbers',
        ),
    ]
