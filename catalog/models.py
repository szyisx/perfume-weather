from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField("Название", max_length=80, unique=True)

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField("Название", max_length=120)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="brands",
        verbose_name="Страна",
    )

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "country"], name="brand_unique_per_country"
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Family(models.Model):
    """Семейство ароматов: цитрусовые, восточные, древесные и т.п."""

    name = models.CharField("Название", max_length=80, unique=True)
    slug = models.SlugField("Слаг", max_length=80, unique=True, blank=True)

    class Meta:
        verbose_name = "Семейство"
        verbose_name_plural = "Семейства"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Note(models.Model):
    """Нота: роза, ваниль, бергамот..."""

    class NoteType(models.TextChoices):
        TOP = "top", "Верхняя"
        HEART = "heart", "Сердечная"
        BASE = "base", "Базовая"

    name = models.CharField("Название", max_length=80)
    type = models.CharField(
        "Тип", max_length=10, choices=NoteType.choices, default=NoteType.HEART
    )
    slug = models.SlugField("Слаг", max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Нота"
        verbose_name_plural = "Ноты"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "type"], name="note_unique_name_type"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.type}", allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_type_display()})"


class Perfume(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"
        UNISEX = "unisex", "Унисекс"

    class Longevity(models.TextChoices):
        WEAK = "weak", "Слабая"
        MEDIUM = "medium", "Средняя"
        STRONG = "strong", "Сильная"

    name = models.CharField("Название", max_length=160)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="perfumes",
        verbose_name="Бренд",
    )
    year = models.PositiveIntegerField(
        "Год выпуска",
        validators=[MinValueValidator(1800), MaxValueValidator(2100)],
        null=True,
        blank=True,
    )
    gender = models.CharField(
        "Гендер", max_length=10, choices=Gender.choices, default=Gender.UNISEX
    )
    longevity = models.CharField(
        "Стойкость",
        max_length=10,
        choices=Longevity.choices,
        default=Longevity.MEDIUM,
    )
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="perfumes/", blank=True, null=True)
    families = models.ManyToManyField(
        Family, related_name="perfumes", verbose_name="Семейства", blank=True
    )
    notes = models.ManyToManyField(
        Note, related_name="perfumes", verbose_name="Ноты", blank=True
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Парфюм"
        verbose_name_plural = "Парфюмы"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "brand"], name="perfume_unique_name_per_brand"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.brand.name} — {self.name}"


class Collection(models.Model):
    """Избранные парфюмы пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collection",
        verbose_name="Пользователь",
    )
    perfume = models.ForeignKey(
        Perfume,
        on_delete=models.CASCADE,
        related_name="in_collections",
        verbose_name="Парфюм",
    )
    added_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "Запись коллекции"
        verbose_name_plural = "Коллекция"
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "perfume"], name="collection_unique_user_perfume"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} ← {self.perfume}"
