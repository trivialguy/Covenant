# Generated by Django 4.2.5 on 2023-10-02 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='secret_key',
            field=models.CharField(editable=False, unique=True),
        ),
    ]
