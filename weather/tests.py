from unittest import mock

from django.test import TestCase

from catalog.models import Brand, Country, Family, Perfume

from .models import WeatherRule
from .services import (
    GeoLocation,
    OpenMeteoClient,
    PerfumeRecommender,
    WeatherError,
    WeatherSnapshot,
    classify_condition,
)


class ClassifyConditionTests(TestCase):
    def test_snow_codes_return_snow(self):
        for code in (71, 73, 75, 77, 85, 86):
            self.assertEqual(classify_condition(code, 0), WeatherRule.Condition.SNOW)

    def test_rain_codes_return_rain(self):
        for code in (51, 61, 65, 80, 95):
            self.assertEqual(classify_condition(code, 10), WeatherRule.Condition.RAIN)

    def test_clear_warm_returns_warm(self):
        self.assertEqual(classify_condition(0, 20), WeatherRule.Condition.WARM)

    def test_clear_hot_returns_hot(self):
        self.assertEqual(classify_condition(0, 30), WeatherRule.Condition.HOT)

    def test_clear_cold_returns_cold(self):
        self.assertEqual(classify_condition(0, -10), WeatherRule.Condition.COLD)

    def test_clear_cool_returns_cool(self):
        self.assertEqual(classify_condition(0, 8), WeatherRule.Condition.COOL)

    def test_snow_priority_over_temperature(self):
        self.assertEqual(classify_condition(75, 30), WeatherRule.Condition.SNOW)


class OpenMeteoClientTests(TestCase):
    def test_geocode_raises_when_city_missing(self):
        client = OpenMeteoClient()
        with mock.patch("weather.services.requests.get") as mocked:
            mocked.return_value = mock.Mock(
                json=lambda: {"results": []},
                raise_for_status=lambda: None,
            )
            with self.assertRaises(WeatherError):
                client.geocode("Atlantis")

    def test_fetch_snapshot_assembles_data(self):
        client = OpenMeteoClient()
        location = GeoLocation(name="Москва", country="Россия", latitude=55.0, longitude=37.0)
        current = {
            "temperature_2m": 27.5,
            "weather_code": 0,
            "relative_humidity_2m": 40,
        }
        with mock.patch.object(client, "geocode", return_value=location):
            with mock.patch.object(client, "get_current_weather", return_value=current):
                snapshot = client.fetch_snapshot("Москва")
        self.assertEqual(snapshot.location.name, "Москва")
        self.assertEqual(snapshot.temperature, 27.5)
        self.assertEqual(snapshot.condition, WeatherRule.Condition.HOT)
        self.assertEqual(snapshot.description, "Ясно")


class PerfumeRecommenderTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Италия")
        self.brand = Brand.objects.create(name="Brand X", country=self.country)
        self.citrus = Family.objects.create(name="Цитрусовые", slug="citrus")
        self.warm = Family.objects.create(name="Восточные", slug="oriental")
        self.fresh = Family.objects.create(name="Свежие", slug="fresh")

        self.summer_perfume = Perfume.objects.create(name="Sun A", brand=self.brand)
        self.summer_perfume.families.set([self.citrus, self.fresh])

        self.winter_perfume = Perfume.objects.create(name="Snow A", brand=self.brand)
        self.winter_perfume.families.set([self.warm])

        WeatherRule.objects.create(
            condition=WeatherRule.Condition.HOT,
            temp_min=25,
            temp_max=50,
            family=self.citrus,
        )
        WeatherRule.objects.create(
            condition=WeatherRule.Condition.HOT,
            temp_min=25,
            temp_max=50,
            family=self.fresh,
        )
        WeatherRule.objects.create(
            condition=WeatherRule.Condition.COLD,
            temp_min=-30,
            temp_max=5,
            family=self.warm,
        )

    def _snapshot(self, temperature: float, condition: str) -> WeatherSnapshot:
        return WeatherSnapshot(
            location=GeoLocation(name="Test", country="", latitude=0, longitude=0),
            temperature=temperature,
            humidity=None,
            weather_code=0,
            condition=condition,
            description="Тест",
        )

    def test_hot_snapshot_returns_summer_perfume_only(self):
        snapshot = self._snapshot(30, WeatherRule.Condition.HOT)
        perfumes, families = PerfumeRecommender().recommend(snapshot)
        names = [p.name for p in perfumes]
        self.assertIn("Sun A", names)
        self.assertNotIn("Snow A", names)
        family_names = {f.name for f in families}
        self.assertSetEqual(family_names, {"Цитрусовые", "Свежие"})

    def test_cold_snapshot_returns_winter_perfume(self):
        snapshot = self._snapshot(-5, WeatherRule.Condition.COLD)
        perfumes, _ = PerfumeRecommender().recommend(snapshot)
        names = [p.name for p in perfumes]
        self.assertIn("Snow A", names)
        self.assertNotIn("Sun A", names)

    def test_empty_when_no_rule_matches(self):
        snapshot = self._snapshot(10, WeatherRule.Condition.WARM)
        perfumes, families = PerfumeRecommender().recommend(snapshot)
        self.assertEqual(list(perfumes), [])
        self.assertEqual(families, [])
