# Generated by Django 3.1.8 on 2022-01-24 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.CharField(max_length=20)),
                ('numbers', models.CharField(max_length=200)),
            ],
        ),
    ]