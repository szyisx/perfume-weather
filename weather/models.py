from django.db import models


class WeatherRule(models.Model):
    """Правило подбора: погода → семейство парфюма."""

    class Condition(models.TextChoices):
        HOT = "hot", "Жара"
        WARM = "warm", "Тепло"
        COOL = "cool", "Прохлада"
        COLD = "cold", "Холод"
        RAIN = "rain", "Дождь"
        SNOW = "snow", "Снег"
        ANY = "any", "Любая"

    condition = models.CharField(
        "Условие", max_length=10, choices=Condition.choices, default=Condition.ANY
    )
    temp_min = models.FloatField("Температура от, °C", default=-50)
    temp_max = models.FloatField("Температура до, °C", default=50)
    family = models.ForeignKey(
        "catalog.Family",
        on_delete=models.CASCADE,
        related_name="weather_rules",
        verbose_name="Семейство",
    )

    class Meta:
        verbose_name = "Правило погоды"
        verbose_name_plural = "Правила погоды"
        ordering = ["condition", "temp_min"]

    def __str__(self) -> str:
        return (
            f"{self.get_condition_display()} "
            f"[{self.temp_min}..{self.temp_max}°C] → {self.family.name}"
        )
