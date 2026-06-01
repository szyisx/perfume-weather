"""Сервисы для интеграции с Open-Meteo и подбора парфюмов по погоде."""

from __future__ import annotations

from dataclasses import dataclass

import requests
from django.db.models import Count, Q, QuerySet

from catalog.models import Family, Perfume

from .models import WeatherRule


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HTTP_TIMEOUT = 6


class WeatherError(Exception):
    """Ошибки при работе с погодным API."""


@dataclass(frozen=True)
class GeoLocation:
    name: str
    country: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class WeatherSnapshot:
    location: GeoLocation
    temperature: float
    humidity: float | None
    weather_code: int
    condition: str
    description: str


WEATHER_CODE_LABELS: dict[int, str] = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Изморозь",
    51: "Слабая морось",
    53: "Морось",
    55: "Сильная морось",
    61: "Слабый дождь",
    63: "Дождь",
    65: "Сильный дождь",
    66: "Ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Слабый снег",
    73: "Снег",
    75: "Сильный снег",
    77: "Снежная крупа",
    80: "Слабый ливень",
    81: "Ливень",
    82: "Сильный ливень",
    85: "Слабый снежный ливень",
    86: "Сильный снежный ливень",
    95: "Гроза",
    96: "Гроза с градом",
    99: "Сильная гроза с градом",
}


def classify_condition(weather_code: int, temperature: float) -> str:
    """Маппинг WMO кода + температуры → одно из условий WeatherRule.Condition."""

    if weather_code in {71, 73, 75, 77, 85, 86}:
        return WeatherRule.Condition.SNOW
    if weather_code in {51, 53, 55, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}:
        return WeatherRule.Condition.RAIN
    if temperature >= 25:
        return WeatherRule.Condition.HOT
    if temperature >= 15:
        return WeatherRule.Condition.WARM
    if temperature >= 5:
        return WeatherRule.Condition.COOL
    return WeatherRule.Condition.COLD


class OpenMeteoClient:
    """Тонкий клиент Open-Meteo Geocoding + Forecast API."""

    def geocode(self, city: str) -> GeoLocation:
        try:
            response = requests.get(
                GEOCODE_URL,
                params={"name": city, "count": 1, "language": "ru", "format": "json"},
                timeout=HTTP_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WeatherError(f"Не удалось обратиться к Geocoding API: {exc}") from exc

        results = response.json().get("results") or []
        if not results:
            raise WeatherError(f"Город «{city}» не найден.")

        first = results[0]
        return GeoLocation(
            name=first.get("name", city),
            country=first.get("country", ""),
            latitude=first["latitude"],
            longitude=first["longitude"],
        )

    def get_current_weather(self, location: GeoLocation) -> dict:
        try:
            response = requests.get(
                FORECAST_URL,
                params={
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "current": "temperature_2m,weather_code,relative_humidity_2m",
                    "timezone": "auto",
                },
                timeout=HTTP_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WeatherError(f"Не удалось получить прогноз: {exc}") from exc

        current = response.json().get("current")
        if not current:
            raise WeatherError("Open-Meteo не вернул данных о текущей погоде.")
        return current

    def fetch_snapshot(self, city: str) -> WeatherSnapshot:
        location = self.geocode(city)
        current = self.get_current_weather(location)

        temperature = float(current["temperature_2m"])
        humidity = current.get("relative_humidity_2m")
        weather_code = int(current["weather_code"])
        condition = classify_condition(weather_code, temperature)
        description = WEATHER_CODE_LABELS.get(weather_code, "Неизвестно")

        return WeatherSnapshot(
            location=location,
            temperature=temperature,
            humidity=float(humidity) if humidity is not None else None,
            weather_code=weather_code,
            condition=condition,
            description=description,
        )


class PerfumeRecommender:
    """Подбор парфюмов по WeatherSnapshot."""

    DEFAULT_LIMIT = 10

    def families_for(self, snapshot: WeatherSnapshot) -> QuerySet[Family]:
        rules = WeatherRule.objects.filter(
            condition__in=[snapshot.condition, WeatherRule.Condition.ANY],
            temp_min__lte=snapshot.temperature,
            temp_max__gte=snapshot.temperature,
        )
        family_ids = list(rules.values_list("family_id", flat=True))
        return Family.objects.filter(id__in=family_ids).distinct()

    def recommend(
        self, snapshot: WeatherSnapshot, limit: int = DEFAULT_LIMIT
    ) -> tuple[QuerySet[Perfume], list[Family]]:
        families = list(self.families_for(snapshot))
        if not families:
            return Perfume.objects.none(), []

        family_ids = [f.id for f in families]
        perfumes = (
            Perfume.objects.filter(families__in=family_ids)
            .select_related("brand")
            .prefetch_related("families")
            .annotate(match_score=Count("families", filter=Q(families__in=family_ids)))
            .order_by("-match_score", "-created_at")
            .distinct()[:limit]
        )
        return perfumes, families
