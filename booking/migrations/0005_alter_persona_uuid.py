# Generated by Django 4.1 on 2023-05-13 21:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0004_alter_persona_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="persona",
            name="uuid",
            field=models.UUIDField(
                auto_created=True,
                default=uuid.UUID("588936a7-c07a-4254-a20c-a5550d8dbfec"),
                primary_key=True,
                serialize=False,
            ),
        ),
    ]