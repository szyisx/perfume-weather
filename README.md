# PerfumeWeather

Веб-приложение на Django для подбора парфюма по текущей погоде. Юзер вводит город — система запрашивает Open-Meteo, классифицирует погоду и предлагает подходящие ароматы по правилам "погода → семейство парфюма".

**Репозиторий:** https://github.com/szyisx/perfume-weather

---

## Стек

- **Backend:** Python 3.10+, Django 6.0
- **БД:** SQLite
- **Frontend:** Bootstrap 5, Bootstrap Icons, Cormorant Garamond + Inter
- **API:** Open-Meteo (Geocoding + Forecast, без ключа)
- **Тесты:** Django TestCase (12 юнит-тестов)
- **VCS:** Git + GitHub

---

## Быстрый старт

```bash
git clone https://github.com/szyisx/perfume-weather.git
cd perfume-weather

python3 -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata fixtures/initial.json
python manage.py createsuperuser
python manage.py runserver
```

Открыть http://127.0.0.1:8000/

**Демо-логин админа** (если использовался `seed_demo`):
`admin` / `admin12345`

---

## Структура проекта

```
perfume-weather/
├── config/             # settings, urls, wsgi/asgi
├── catalog/            # парфюмы, бренды, ноты, семейства, коллекция
│   ├── models.py
│   ├── views.py        # CBV ListView/DetailView + CRUD
│   ├── forms.py        # PerfumeForm
│   └── management/commands/seed_demo.py
├── accounts/           # кастомный User, регистрация, профиль
├── weather/            # WeatherRule + сервисы Open-Meteo
│   ├── services.py     # OpenMeteoClient, classify_condition, PerfumeRecommender
│   ├── views.py        # recommend_view
│   └── tests.py        # 12 юнит-тестов
├── templates/          # HTML шаблоны
├── static/css/         # main.css (кастомная тёмная палитра)
├── fixtures/initial.json
├── docs/ER.md          # ER-диаграмма (Mermaid + DBML)
├── DEMO.md             # сценарий защиты
└── PLAN.md             # план разработки
```

---

## Ключевая фича — алгоритм подбора

```
город
  ↓ Open-Meteo Geocoding API
координаты
  ↓ Open-Meteo Forecast API
{ temperature, weather_code, humidity }
  ↓ classify_condition()
condition ∈ { hot, warm, cool, cold, rain, snow }
  ↓ WeatherRule.filter(condition, temp_min ≤ T ≤ temp_max)
[ Family, Family, ... ]
  ↓ Perfume.filter(families__in=...) + match_score annotation
top-10 perfumes
```

**Пример:**
- Москва, +27°C, ясно → `hot` → Цитрусовые + Свежие → 4 парфюма
- Якутск, -25°C, снег → `snow` → Восточные → 3 парфюма
- Ереван, +12°C, дождь → `rain` → Древесные → 2 парфюма

См. `weather/services.py` и `docs/ER.md`.

---

## Тесты

```bash
python manage.py test
```

12 тестов: `classify_condition` для всех условий, моки `OpenMeteoClient`, выборка парфюмов `PerfumeRecommender`.

---

## Скриншоты

Скриншоты приложить вручную перед сдачей. Рекомендуемые страницы:
- Главная (hero + форма)
- Каталог с фильтрами
- Детальная парфюма (пирамида нот)
- Профиль с коллекцией
- Подбор по погоде (результат для разных городов)
- Админка

---

## Этапы разработки

См. [PLAN.md](PLAN.md), [DEMO.md](DEMO.md), [GUIDE.md](GUIDE.md) (для защиты, объясняет проект на простом языке).

- [x] Этап 0. Подготовка (репо, venv, .gitignore)
- [x] Этап 1. [ER-диаграмма](docs/ER.md)
- [x] Этап 2. Каркас + модели + миграции
- [x] Этап 3. Шаблоны + статика (Bootstrap 5)
- [x] Этап 4. Просмотр данных (ListView / DetailView)
- [x] Этап 5. Формы + CRUD (ModelForm, Create/Update/DeleteView)
- [x] Этап 6. Авторизация (регистрация, login, профиль, права)
- [x] Этап 7. Подбор по погоде (Open-Meteo + правила)
- [x] Этап 8. Финал (fixtures, README, DEMO)

---

## Лицензия

Учебный проект. Все права на торговые марки парфюмерных брендов в демо-данных принадлежат их владельцам. Имена в `seed_demo.py` — вымышленные.
