# Generated by Django 4.2.5 on 2023-09-27 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Vote', models.CharField()),
                ('address', models.CharField()),
                ('secret_key', models.CharField(unique=True)),
            ],
        ),
    ]
