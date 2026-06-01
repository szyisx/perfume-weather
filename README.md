# PerfumeWeather

Веб-приложение для подбора парфюма по текущей погоде. Учитывает температуру, влажность и погодные условия для рекомендации подходящих ароматов.

## Идея

Юзер вводит город → API погоды (Open-Meteo) возвращает текущие условия → система сопоставляет погоду с семействами парфюмов через правила → выводит топ рекомендаций.

## Стек

- **Backend:** Python 3.10+, Django 5
- **БД:** SQLite
- **Frontend:** Bootstrap 5, Django Templates
- **API:** Open-Meteo (погода + геокодинг)
- **VCS:** Git + GitHub

## Структура проекта

```
perfume-weather/
├── config/         # Настройки Django (settings, urls)
├── catalog/        # Парфюмы, бренды, ноты, семейства
├── accounts/       # Пользователи, регистрация
├── weather/        # Логика погоды и подбора
├── templates/      # HTML шаблоны
├── static/         # CSS, JS, изображения
├── media/          # Загруженные изображения парфюмов
└── manage.py
```

## Запуск локально

```bash
git clone https://github.com/<user>/perfume-weather.git
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

## Этапы разработки

См. [PLAN.md](PLAN.md).

- [x] Этап 0. Подготовка
- [x] Этап 1. [ER-диаграмма](docs/ER.md)
- [x] Этап 2. Каркас + модели + миграции
- [x] Этап 3. Шаблоны + статика
- [ ] Этап 4. Просмотр данных (CBV)
- [ ] Этап 5. Формы + CRUD
- [ ] Этап 6. Авторизация
- [ ] Этап 7. Подбор по погоде
- [ ] Этап 8. Финал

## Автор

Учебный проект.
