# Generated by Django 4.1 on 2023-05-13 21:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0003_alter_persona_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="persona",
            name="uuid",
            field=models.UUIDField(
                auto_created=True,
                default=uuid.UUID("25dc2fb4-9eaf-476f-b24f-05ae03a84611"),
                primary_key=True,
                serialize=False,
            ),
        ),
    ]