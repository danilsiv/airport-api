from django.db import models


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    iata_code = models.CharField(max_length=3, unique=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="airports"
    )

    class Meta:
        ordering = ("city__country", "city__name", "name")

    def __str__(self) -> str:
        return f"{self.name} {self.iata_code}"
