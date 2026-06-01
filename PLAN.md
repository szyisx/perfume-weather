# PerfumeWeather — План проекта

**Идея:** подбор парфюма по текущей погоде (Open-Meteo API → семейства парфюмов → выборка).

**Стек:** Python 3.10+, Django 5, SQLite, Bootstrap 5, Open-Meteo API, Git/GitHub.

---

## Этап 0. Подготовка (день 1)

- [ ] Установить Python 3.10+, VS Code, Git
- [ ] Создать GitHub репозиторий `perfume-weather`
- [ ] Клонировать локально в `~/PROJECTS/Python/perfume-weather`
- [ ] Создать `.gitignore` (venv, __pycache__, db.sqlite3, .env, media/)
- [ ] Создать `README.md` с описанием
- [ ] Первый коммит: `chore: init repo`

---

## Этап 1. ER-диаграмма (готово, нужны правки)

**Финальная схема (после правок):**

| Таблица | Поля |
|---------|------|
| `User` (AbstractUser) | id, username, email, password (Django auth) |
| `Country` | id, name |
| `Brand` | id, name, country_id FK |
| `Family` | id, name, slug |
| `Note` | id, name, type (top/heart/base), slug |
| `Perfume` | id, name, brand_id FK, year, gender, longevity, description, image, created_at |
| `PerfumeFamily` (M:M) | id, perfume_id FK, family_id FK |
| `PerfumeNote` (M:M) | id, perfume_id FK, note_id FK |
| `WeatherRule` | id, condition, temp_min, temp_max, family_id FK |
| `Collection` (избранное) | id, user_id FK, perfume_id FK, added_at |

**Правки от исходной:**
- Убрать `Perfume.family_id` и `Perfume.note_id` (дубль M:M)
- Убрать свой `User` → использовать Django `AbstractUser`
- Добавить `WeatherRule` (связь погода→семейство)
- Упростить `Collection` (убрать status/notes)
- Добавить `description`, `image`, `created_at` на `Perfume`

**Сдача:** скриншот ER в draw.io, утверждена.

---

## Этап 2. Каркас + модели + миграции (день 2-3)

### Команды старта:
```bash
cd ~/PROJECTS/Python/perfume-weather
python3 -m venv venv
source venv/bin/activate
pip install django pillow requests python-dotenv
pip freeze > requirements.txt
django-admin startproject config .
python manage.py startapp catalog
python manage.py startapp accounts
python manage.py startapp weather
```

### Структура:
```
perfume-weather/
├── config/         # settings, urls, wsgi
├── catalog/        # Perfume, Brand, Family, Note, Collection
├── accounts/       # User, регистрация
├── weather/        # WeatherRule, Open-Meteo клиент
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```

### Settings:
- `INSTALLED_APPS` += catalog, accounts, weather
- `AUTH_USER_MODEL = 'accounts.User'`
- `MEDIA_URL`, `MEDIA_ROOT`
- `STATICFILES_DIRS`
- `TEMPLATES.DIRS = [BASE_DIR / 'templates']`

### Команды:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Зарегистрировать модели в `admin.py` всех приложений.

### Тестовые данные:
- 3 страны (Франция, США, Италия)
- 5 брендов
- 5 семейств (восточные, цветочные, цитрусовые, древесные, свежие)
- 15 нот
- 10 парфюмов с привязкой к семействам/нотам
- 5 правил погоды

**Сдача:** проект запускается, админка с данными, коммит на GitHub.

---

## Этап 3. Шаблоны + статика (день 4)

### Создать:
- [ ] `templates/base.html` — навбар, footer, Bootstrap CDN
- [ ] `templates/home.html` — главная (форма погоды + результат)
- [ ] `templates/catalog/perfume_list.html` — все парфюмы
- [ ] `templates/catalog/perfume_detail.html` — карточка
- [ ] `templates/accounts/login.html`, `register.html`
- [ ] `templates/collection/list.html` — мои избранные

### Подключить Bootstrap 5 через CDN в `base.html`.

### Навбар: Главная / Каталог / Моя коллекция / Войти/Выйти.

**Сдача:** дизайн единый, навигация работает, заглушки открываются.

---

## Этап 4. Просмотр данных (CBV) (день 5)

### `catalog/views.py`:
- `PerfumeListView(ListView)` — список с пагинацией (12/стр)
- `PerfumeDetailView(DetailView)` — детальная

### `catalog/urls.py`:
```python
path('perfumes/', PerfumeListView.as_view(), name='perfume_list'),
path('perfumes/<int:pk>/', PerfumeDetailView.as_view(), name='perfume_detail'),
```

### Фильтры в списке: по бренду, семейству, гендеру (GET-параметры).

### Шаблоны: показать имя, бренд, семейства, ноты, изображение.

**Сдача:** список + детальная с реальными данными.

---

## Этап 5. Формы + CRUD (день 6-7)

### Что: CRUD парфюмов (только для админа/superuser).

### Views:
- `PerfumeCreateView` (LoginRequiredMixin + UserPassesTestMixin)
- `PerfumeUpdateView`
- `PerfumeDeleteView`

### `forms.py`:
```python
class PerfumeForm(ModelForm):
    class Meta:
        model = Perfume
        fields = ['name', 'brand', 'year', 'gender', 'longevity', 'families', 'notes', 'image', 'description']
        widgets = {'families': CheckboxSelectMultiple, 'notes': CheckboxSelectMultiple}
```

### Валидация: `year >= 1900`, `name` уникальный в бренде.

### CRUD для коллекции (избранное):
- Добавить в избранное (POST из карточки)
- Удалить из избранного

**Сдача:** создание/редактирование/удаление работает.

---

## Этап 6. Авторизация + права (день 8)

### `accounts/`:
- [ ] `RegisterView(CreateView)` с `UserCreationForm`
- [ ] LoginView / LogoutView из `django.contrib.auth.views`
- [ ] `ProfileView` — профиль пользователя со своей коллекцией

### URLs:
```python
path('register/', RegisterView.as_view(), name='register'),
path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
path('logout/', LogoutView.as_view(), name='logout'),
path('profile/', ProfileView.as_view(), name='profile'),
```

### Права:
- Просмотр каталога — все
- Добавление в коллекцию — `@login_required`
- CRUD парфюмов — `is_staff`
- Своя коллекция — только владелец видит

### `Collection.objects.filter(user=request.user)` — фильтр по юзеру.

**Сдача:** регистрация/вход работают, каждый видит свою коллекцию.

---

## Этап 7. Уникальная фича — подбор по погоде (день 9-10)

### Архитектура:
```
weather/services.py
├── OpenMeteoClient — запрос к API
├── WeatherMatcher — погода → семейства → парфюмы
└── PerfumeRecommender — финальная выборка
```

### `weather/services.py`:
```python
import requests

class OpenMeteoClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def get_current(self, lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,relative_humidity_2m",
        }
        r = requests.get(self.BASE_URL, params=params, timeout=5)
        r.raise_for_status()
        return r.json()["current"]
```

### Логика матчинга:
1. Юзер вводит город (или геолокация через JS)
2. Город → координаты (Open-Meteo Geocoding API)
3. Координаты → погода (температура, код погоды, влажность)
4. Погода → `WeatherRule` → семейства
5. Семейства → `Perfume` (через M:M)
6. Вывод 5-10 рекомендаций

### View:
```python
class RecommendView(View):
    def post(self, request):
        city = request.POST.get('city')
        weather = OpenMeteoClient().get_by_city(city)
        rules = WeatherRule.objects.filter(
            temp_min__lte=weather['temp'],
            temp_max__gte=weather['temp'],
            condition=weather['code'],
        )
        families = [r.family for r in rules]
        perfumes = Perfume.objects.filter(families__in=families).distinct()[:10]
        return render(request, 'recommend.html', {'perfumes': perfumes, 'weather': weather})
```

### Шаблон: показывает текущую погоду + 10 парфюмов с объяснением "почему подходит".

### Тестовые правила (примеры):
| Условие | Температура | Семейство |
|---------|-------------|-----------|
| Жара | 25-50 | Цитрусовые, Свежие |
| Тепло | 15-25 | Цветочные |
| Холод | -10-10 | Восточные, Древесные |
| Дождь | любая | Древесные |

**Сдача:** записать видео работы фичи.

---

## Этап 8. Финал (день 11)

- [ ] README с скриншотами и инструкцией запуска
- [ ] requirements.txt актуальный
- [ ] Все этапы закоммичены отдельно
- [ ] Тестовые данные через fixtures (`dumpdata`/`loaddata`)
- [ ] Защита: ER + демонстрация всех этапов

---

## Соглашения по коммитам

```
feat: add WeatherRule model and migration
feat: implement Open-Meteo client
fix: correct M:M for perfume families
docs: update README with setup steps
```

Один этап = минимум 1 коммит. После каждого этапа — push.

---

## Структура README.md

```markdown
# PerfumeWeather
Подбор парфюма по погоде.

## Стек
Django 5, SQLite, Bootstrap, Open-Meteo API.

## Запуск
1. git clone ...
2. python -m venv venv && source venv/bin/activate
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py loaddata fixtures/initial.json
6. python manage.py createsuperuser
7. python manage.py runserver
```

---

## Следующий шаг

Этап 0: создание репо, venv, базовая структура.
