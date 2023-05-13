# Generated by Django 4.1 on 2023-05-11 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=500)),
                ("gpt", models.CharField(max_length=17000)),
                ("date", models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
