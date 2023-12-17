# Generated by Django 4.1 on 2023-12-17 22:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Census",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("voting_id", models.PositiveIntegerField()),
                ("voter_id", models.PositiveIntegerField()),
                (
                    "role",
                    models.CharField(
                        choices=[
                            (
                                "0",
                                "Only for Hierchical Votings. Select this if voting isn`t Hierchical",
                            ),
                            ("1", "Balanceado"),
                            ("2", "Colaborador"),
                            ("3", "Coordinador"),
                            ("4", "Presidente"),
                        ],
                        default="0",
                        max_length=1,
                    ),
                ),
            ],
            options={
                "unique_together": {("voting_id", "voter_id")},
            },
        ),
    ]
