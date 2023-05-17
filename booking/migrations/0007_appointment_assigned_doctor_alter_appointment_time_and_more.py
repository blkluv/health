# Generated by Django 4.1 on 2023-05-17 10:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0006_alter_appointment_service_alter_doctor_role_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="assigned_doctor",
            field=models.CharField(default="", editable=False, max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="appointment",
            name="time",
            field=models.CharField(
                choices=[
                    ("8 AM", "8 AM"),
                    ("9 AM", "9 AM"),
                    ("10 AM", "10 AM"),
                    ("11 AM", "11 AM"),
                    ("11:30 AM", "11:30 AM"),
                    ("12 PM", "12 PM"),
                    ("1:30 PM", "1:30 PM"),
                    ("2 PM", "2 PM"),
                ],
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="persona",
            name="uuid",
            field=models.UUIDField(
                auto_created=True,
                default=uuid.UUID("67cf2161-3553-456f-9a6d-92be59d3b2ff"),
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
