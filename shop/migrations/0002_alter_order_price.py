# Generated by Django 5.1.3 on 2024-11-19 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="price",
            field=models.FloatField(),
        ),
    ]
