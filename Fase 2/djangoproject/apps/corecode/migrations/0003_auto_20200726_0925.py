# Generated by Django 3.0.7 on 2020-07-26 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corecode", "0002_auto_20200506_1520"),
    ]

    operations = [
        migrations.AlterField(
            model_name="academicsession",
            name="current",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name="academicterm",
            name="current",
            field=models.BooleanField(default=False, null=True),
        ),
    ]