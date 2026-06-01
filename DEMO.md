# Сценарий защиты PerfumeWeather

Гайд для устной демонстрации проекта по этапам.

---

## 0. Подготовка перед защитой

```bash
cd ~/PROJECTS/Python/perfume-weather
source venv/bin/activate
python manage.py migrate
python manage.py loaddata fixtures/initial.json
python manage.py createsuperuser   # admin / admin12345 (если ещё нет)
python manage.py runserver
```

Открыть http://127.0.0.1:8000/ в браузере.

---

## Этап 1. ER-диаграмма

**Показать:** `docs/ER.md` на GitHub (Mermaid рендерится автоматически).

**Рассказать:**
- 10 сущностей: User, Country, Brand, Family, Note, Perfume, PerfumeFamily (M:M), PerfumeNote (M:M), WeatherRule, Collection
- Связи 1:M (Country→Brand, Brand→Perfume) и M:M (Perfume↔Family, Perfume↔Note)
- Кастомный User через `AbstractUser`
- `WeatherRule` — ядро фичи, связывает погоду с семействами

---

## Этап 2. Каркас + модели + миграции

**Показать:**
```bash
ls config/ catalog/ accounts/ weather/
cat catalog/models.py
python manage.py showmigrations
```

**Рассказать:**
- 3 приложения: `catalog`, `accounts`, `weather`
- `INSTALLED_APPS`, `AUTH_USER_MODEL`, `MEDIA_*`, `STATICFILES_DIRS`
- Unique constraints: бренд в стране, парфюм в бренде, коллекция (user, perfume)
- `seed_demo` management command

**Открыть админку:** http://127.0.0.1:8000/admin/ (admin / admin12345)
- Показать все модели
- Открыть Perfume → `filter_horizontal` для families/notes

---

## Этап 3. Шаблоны + статика

**Показать:**
```bash
ls templates/ static/css/
```

**Открыть:** главную http://127.0.0.1:8000/
- Тёмный editorial-дизайн
- Bootstrap 5 + Bootstrap Icons + Cormorant Garamond + Inter
- Sticky-навбар, hero-секция

---

## Этап 4. Просмотр данных (CBV)

**Открыть:** http://127.0.0.1:8000/perfumes/
- 10 парфюмов из БД
- Фильтры: `?q=`, `?brand=`, `?family=`, `?gender=`
- Пагинация (12/стр)
- Кликнуть на карточку → детальная страница
- Показать пирамиду нот (`{% regroup %}` по type)

**Код:** `catalog/views.py` — `PerfumeListView`, `PerfumeDetailView`
- `select_related` + `prefetch_related` против N+1

---

## Этап 5. Формы + CRUD

**Показать создание парфюма (как admin):**
1. Логин: http://127.0.0.1:8000/login/ (admin / admin12345)
2. http://127.0.0.1:8000/perfumes/new/
3. Заполнить форму → создать
4. На детальной странице → "Редактировать" → изменить → сохранить
5. "Удалить" → подтверждение → удалить

**Показать коллекцию:**
1. Открыть любой парфюм → "В коллекцию"
2. http://127.0.0.1:8000/collection/ — карточка появилась
3. "Убрать" → исчезла

**Код:**
- `catalog/forms.py` — `PerfumeForm(ModelForm)` с валидацией `year >= 1900`
- `StaffRequiredMixin` (LoginRequired + UserPassesTest)
- `collection_add` / `collection_remove` (@login_required + @require_POST)

---

## Этап 6. Авторизация + права

**Регистрация нового юзера:**
1. Logout
2. http://127.0.0.1:8000/register/
3. Создать `testuser` / `Pa$$word123`
4. Авто-логин → редирект на главную
5. http://127.0.0.1:8000/profile/ — профиль (аватарка, дата регистрации)

**Проверка прав:**
1. Под `testuser` (не staff) попытка http://127.0.0.1:8000/perfumes/new/ → **403 Forbidden**
2. Аноним → http://127.0.0.1:8000/collection/ → редирект на login

**Код:**
- `accounts/forms.py` — `UserRegisterForm(UserCreationForm)`
- `accounts/views.py` — `RegisterView`, `profile_view`
- `accounts/urls.py` — `LoginView`/`LogoutView` из `django.contrib.auth.views`
- `Collection.objects.filter(user=request.user)` — фильтрация по юзеру

---

## Этап 7. Уникальная фича — подбор по погоде

**Запустить вживую:**
1. http://127.0.0.1:8000/recommend/
2. Ввести "Москва" → подобрать
3. Показывается карточка погоды (температура, описание, условие) + чипы семейств + сетка парфюмов
4. Попробовать "Дубай" (жара → цитрусовые/свежие)
5. Попробовать "Якутск" (холод → восточные/древесные)
6. Попробовать "AtlantisXYZ" → alert "город не найден"

**Рассказать архитектуру:**
- `weather/services.py`:
  - `OpenMeteoClient` — Geocoding + Forecast API (без ключа)
  - `classify_condition(code, temp)` — WMO код → hot/warm/cool/cold/rain/snow
  - `PerfumeRecommender` — snapshot → правила → семейства → парфюмы с `match_score`
- 12 юнит-тестов: `python manage.py test weather`

**Алгоритм матчинга:**
```
город
  → Geocoding API → координаты
  → Forecast API → температура + weather_code
  → classify_condition → condition (hot/cold/...)
  → WeatherRule.filter(condition, temp_min<=t<=temp_max) → семейства
  → Perfume.filter(families__in=...) → топ-10 по match_score
```

---

## Бонус: команды

| Команда | Эффект |
|---------|--------|
| `python manage.py migrate` | Применить миграции |
| `python manage.py seed_demo` | Заполнить БД демо-данными |
| `python manage.py loaddata fixtures/initial.json` | Загрузить fixture |
| `python manage.py test` | Прогнать все тесты |
| `python manage.py createsuperuser` | Создать админа |
| `python manage.py runserver` | Запустить сервер |

---

## Чек-лист защиты

- [ ] Сервер запущен (`runserver`)
- [ ] Тестовые данные загружены (loaddata или seed_demo)
- [ ] Админка работает (admin / admin12345)
- [ ] testuser создан и проверен 403
- [ ] Интернет есть для Open-Meteo
- [ ] GitHub репо открыт в браузере для показа кода
