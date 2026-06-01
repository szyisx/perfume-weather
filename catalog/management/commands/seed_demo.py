"""Команда `manage.py seed_demo` — заполняет БД тестовыми данными."""

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Brand, Country, Family, Note, Perfume
from weather.models import WeatherRule


COUNTRIES = ["Франция", "Италия", "США", "ОАЭ"]

BRANDS = [
    ("Maison Aurea", "Франция"),
    ("Pellegrino Profumi", "Италия"),
    ("Northshore Lab", "США"),
    ("Dunes Couture", "ОАЭ"),
    ("Ateliér Verde", "Франция"),
]

FAMILIES = [
    "Цитрусовые",
    "Цветочные",
    "Фруктовые",
    "Древесные",
    "Восточные",
    "Свежие",
    "Зелёные",
]

NOTES = [
    ("Бергамот", "top"),
    ("Лимон", "top"),
    ("Грейпфрут", "top"),
    ("Роза", "heart"),
    ("Жасмин", "heart"),
    ("Иланг-иланг", "heart"),
    ("Яблоко", "heart"),
    ("Ваниль", "base"),
    ("Сандал", "base"),
    ("Кедр", "base"),
    ("Пачули", "base"),
    ("Уд", "base"),
    ("Морская соль", "top"),
    ("Мята", "top"),
    ("Дубовый мох", "base"),
]

PERFUMES = [
    {
        "name": "Citrus Dawn",
        "brand": "Maison Aurea",
        "year": 2021,
        "gender": "unisex",
        "longevity": "medium",
        "description": "Лёгкий цитрусовый старт с акцентом на бергамот и грейпфрут.",
        "families": ["Цитрусовые", "Свежие"],
        "notes": ["Бергамот", "Грейпфрут", "Мята", "Кедр"],
    },
    {
        "name": "Velvet Rose",
        "brand": "Pellegrino Profumi",
        "year": 2019,
        "gender": "female",
        "longevity": "strong",
        "description": "Глубокая роза с тёплой ванилью и сандалом.",
        "families": ["Цветочные", "Восточные"],
        "notes": ["Роза", "Ваниль", "Сандал"],
    },
    {
        "name": "Oud Sahara",
        "brand": "Dunes Couture",
        "year": 2022,
        "gender": "unisex",
        "longevity": "strong",
        "description": "Восточный аромат с удом и тёмной древесиной.",
        "families": ["Восточные", "Древесные"],
        "notes": ["Уд", "Сандал", "Пачули"],
    },
    {
        "name": "Pacific Wave",
        "brand": "Northshore Lab",
        "year": 2023,
        "gender": "male",
        "longevity": "medium",
        "description": "Морская свежесть с цитрусовой ноткой.",
        "families": ["Свежие", "Цитрусовые"],
        "notes": ["Морская соль", "Лимон", "Кедр"],
    },
    {
        "name": "Forest Pulse",
        "brand": "Ateliér Verde",
        "year": 2020,
        "gender": "unisex",
        "longevity": "strong",
        "description": "Зелёный древесный аромат с мхом и кедром.",
        "families": ["Зелёные", "Древесные"],
        "notes": ["Дубовый мох", "Кедр", "Пачули"],
    },
    {
        "name": "Apple Bloom",
        "brand": "Maison Aurea",
        "year": 2022,
        "gender": "female",
        "longevity": "medium",
        "description": "Сочное яблоко и нежные цветочные ноты.",
        "families": ["Фруктовые", "Цветочные"],
        "notes": ["Яблоко", "Жасмин", "Иланг-иланг"],
    },
    {
        "name": "Solar Mint",
        "brand": "Northshore Lab",
        "year": 2024,
        "gender": "unisex",
        "longevity": "weak",
        "description": "Освежающая мята и цитрус для жаркого дня.",
        "families": ["Свежие", "Цитрусовые"],
        "notes": ["Мята", "Лимон", "Бергамот"],
    },
    {
        "name": "Winter Amber",
        "brand": "Pellegrino Profumi",
        "year": 2018,
        "gender": "unisex",
        "longevity": "strong",
        "description": "Тёплая амбра, ваниль и древесина для холодных дней.",
        "families": ["Восточные", "Древесные"],
        "notes": ["Ваниль", "Сандал", "Уд"],
    },
    {
        "name": "Spring Jasmine",
        "brand": "Ateliér Verde",
        "year": 2021,
        "gender": "female",
        "longevity": "medium",
        "description": "Лёгкий весенний жасмин с цитрусовым шлейфом.",
        "families": ["Цветочные", "Зелёные"],
        "notes": ["Жасмин", "Бергамот", "Дубовый мох"],
    },
    {
        "name": "Desert Wood",
        "brand": "Dunes Couture",
        "year": 2020,
        "gender": "male",
        "longevity": "strong",
        "description": "Сухая древесина с пряным удом.",
        "families": ["Древесные", "Восточные"],
        "notes": ["Кедр", "Уд", "Пачули"],
    },
]

WEATHER_RULES = [
    ("hot", 25, 50, "Цитрусовые"),
    ("hot", 25, 50, "Свежие"),
    ("warm", 15, 25, "Цветочные"),
    ("warm", 15, 25, "Фруктовые"),
    ("warm", 15, 25, "Зелёные"),
    ("cool", 5, 15, "Зелёные"),
    ("cool", 5, 15, "Древесные"),
    ("cold", -30, 5, "Восточные"),
    ("cold", -30, 5, "Древесные"),
    ("rain", -50, 50, "Древесные"),
    ("snow", -50, 5, "Восточные"),
]


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными для PerfumeWeather."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Сидинг базы данных...")

        countries = {name: Country.objects.get_or_create(name=name)[0] for name in COUNTRIES}
        self.stdout.write(f"  Страны: {len(countries)}")

        brands = {}
        for name, country in BRANDS:
            brand, _ = Brand.objects.get_or_create(name=name, country=countries[country])
            brands[name] = brand
        self.stdout.write(f"  Бренды: {len(brands)}")

        families = {name: Family.objects.get_or_create(name=name)[0] for name in FAMILIES}
        self.stdout.write(f"  Семейства: {len(families)}")

        notes = {}
        for name, ntype in NOTES:
            note, _ = Note.objects.get_or_create(name=name, type=ntype)
            notes[(name, ntype)] = note
        self.stdout.write(f"  Ноты: {len(notes)}")

        for p in PERFUMES:
            perfume, created = Perfume.objects.get_or_create(
                name=p["name"],
                brand=brands[p["brand"]],
                defaults={
                    "year": p["year"],
                    "gender": p["gender"],
                    "longevity": p["longevity"],
                    "description": p["description"],
                },
            )
            if created:
                perfume.families.set([families[f] for f in p["families"]])
                perfume.notes.set(
                    [note for (nm, _t), note in notes.items() if nm in p["notes"]]
                )
        self.stdout.write(f"  Парфюмы: {Perfume.objects.count()}")

        for cond, tmin, tmax, fam_name in WEATHER_RULES:
            WeatherRule.objects.get_or_create(
                condition=cond,
                temp_min=tmin,
                temp_max=tmax,
                family=families[fam_name],
            )
        self.stdout.write(f"  Правила погоды: {WeatherRule.objects.count()}")

        self.stdout.write(self.style.SUCCESS("Готово."))
