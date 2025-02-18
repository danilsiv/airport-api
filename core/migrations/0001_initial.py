# Generated by Django 5.1.6 on 2025-02-18 12:19

import core.validators
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AirplaneType",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="City",
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
                ("name", models.CharField(max_length=255)),
                ("country", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "cities",
            },
        ),
        migrations.CreateModel(
            name="CrewMember",
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
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ("role__name", "first_name"),
            },
        ),
        migrations.CreateModel(
            name="Order",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Role",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Route",
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
                (
                    "distance",
                    models.IntegerField(
                        help_text="Distance in kilometers",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
            ],
            options={
                "ordering": ("source",),
            },
        ),
        migrations.CreateModel(
            name="SeatConfiguration",
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
                (
                    "seats_class",
                    models.CharField(
                        choices=[
                            ("EC", "Economy Class"),
                            ("BC", "Business Class"),
                            ("FC", "First Class"),
                        ],
                        default="EC",
                        max_length=2,
                    ),
                ),
                (
                    "rows",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "seats_in_row",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
            ],
            options={
                "ordering": (
                    "airplane__model_name",
                    models.Case(
                        models.When(seats_class="EC", then=0),
                        models.When(seats_class="BC", then=1),
                        models.When(seats_class="FC", then=2),
                        output_field=models.IntegerField(),
                    ),
                ),
            },
        ),
        migrations.CreateModel(
            name="Ticket",
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
                ("row", models.IntegerField()),
                ("seat", models.IntegerField()),
                ("passenger_first_name", models.CharField(max_length=255)),
                ("passenger_last_name", models.CharField(max_length=255)),
                (
                    "seat_class",
                    models.CharField(
                        choices=[
                            ("EC", "Economy Class"),
                            ("BC", "Business Class"),
                            ("FC", "First Class"),
                        ],
                        default="EC",
                        max_length=2,
                    ),
                ),
            ],
            options={
                "ordering": ("seat",),
            },
        ),
        migrations.CreateModel(
            name="Airplane",
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
                ("model_name", models.CharField(max_length=255)),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="airplanes",
                        to="core.airplanetype",
                    ),
                ),
            ],
            options={
                "ordering": ("type__name", "model_name"),
            },
        ),
        migrations.CreateModel(
            name="Airport",
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
                ("name", models.CharField(max_length=255)),
                (
                    "iata_code",
                    models.CharField(
                        max_length=3,
                        unique=True,
                        validators=[core.validators.validate_iata_code_format],
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="airports",
                        to="core.city",
                    ),
                ),
            ],
            options={
                "ordering": ("city__country", "city__name", "name"),
            },
        ),
        migrations.CreateModel(
            name="CrewGroup",
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
                (
                    "additional_staff",
                    models.ManyToManyField(
                        blank=True,
                        related_name="additional_staff_crew_groups",
                        to="core.crewmember",
                    ),
                ),
                (
                    "pilots",
                    models.ManyToManyField(
                        blank=True,
                        related_name="pilot_crew_groups",
                        to="core.crewmember",
                    ),
                ),
                (
                    "stewards",
                    models.ManyToManyField(
                        blank=True,
                        related_name="steward_crew_groups",
                        to="core.crewmember",
                    ),
                ),
                (
                    "technicians",
                    models.ManyToManyField(
                        blank=True,
                        related_name="technician_crew_groups",
                        to="core.crewmember",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Flight",
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
                (
                    "flight_number",
                    models.CharField(
                        max_length=7,
                        unique=True,
                        validators=[core.validators.validate_flight_number_format],
                    ),
                ),
                ("departure_time", models.DateTimeField()),
                ("arrival_time", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SD", "Scheduled"),
                            ("AD", "Arrived"),
                            ("CD", "Canceled"),
                        ],
                        default="SD",
                        max_length=2,
                    ),
                ),
                (
                    "airplane",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="flights",
                        to="core.airplane",
                    ),
                ),
                (
                    "crew",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="flight",
                        to="core.crewgroup",
                    ),
                ),
            ],
            options={
                "ordering": (
                    models.Case(
                        models.When(status="SD", then=0),
                        models.When(status="AD", then=1),
                        models.When(status="CD", then=2),
                        output_field=models.IntegerField(),
                    ),
                    "departure_time",
                ),
            },
        ),
    ]
