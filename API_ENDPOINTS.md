# API Endpoints Documentation

## 📦 Core API - Общие данные

### Cities (Города)
- `GET /api/core/cities/` - Список всех активных городов
- `GET /api/core/cities/{id}/` - Детали конкретного города

**Пример ответа:**
```json
{
  "id": 1,
  "name": "Бишкек",
  "is_active": true,
  "order": 1
}
```

### Delivery Zones (Зоны доставки)
- `GET /api/core/delivery-zones/` - Список всех активных зон доставки
- `GET /api/core/delivery-zones/{id}/` - Детали конкретной зоны

**Пример ответа:**
```json
{
  "id": 1,
  "name": "Патонг",
  "price": 500.00,
  "is_active": true,
  "order": 1
}
```

### Rental Providers (Прокатчики)
- `GET /api/core/providers/` - Список всех активных прокатчиков
- `GET /api/core/providers/{id}/` - Детали конкретного прокатчика

**Пример ответа:**
```json
{
  "id": 1,
  "name": "Rental Pro",
  "phone": "+66123456789",
  "email": "",
  "telegram": "",
  "terms": "",
  "notes": "Работаем с 9:00 до 20:00",
  "is_active": true
}
```

### Service Terms (Условия обслуживания)
- `GET /api/core/service-terms/` - Список активных условий обслуживания

**Пример ответа:**
```json
[
  {
    "id": 1,
    "title": "Общие условия аренды",
    "content": "Текст условий...",
    "is_active": true,
    "created_at": "2025-10-26T10:00:00Z"
  }
]
```

---

## 🚗 Cars API - Автомобили

### Cars (Автомобили)
- `GET /api/cars/cars/` - Список всех автомобилей
- `GET /api/cars/cars/{id}/` - Детали конкретного автомобиля

**Пример ответа:**
```json
{
  "id": 1,
  "title": "Toyota Fortuner 2023",
  "description": "Премиум внедорожник",
  "price_per_day": 2500.00,
  "deposit": 10000.00,
  "city": {
    "id": 1,
    "name": "Бишкек"
  },
  "rental_provider": {
    "id": 1,
    "name": "",
    "phone": "",
    "telegram": ""
  },
  "delivery_zones": [
    {
      "id": 1,
      "name": "",
      "price": 500.00
    }
  ],
  "price_tiers": [
    {
      "id": 1,
      "min_days": 1,
      "price_per_day": 2500.00
    },
    {
      "id": 2,
      "min_days": 7,
      "price_per_day": 2000.00
    },
    {
      "id": 3,
      "min_days": 30,
      "price_per_day": 1500.00
    }
  ],
  "brand": {
    "id": 1,
    "name": "Toyota",
    "logo": "/media/cars/brands/toyota.png"
  },
  "model": {
    "id": 1,
    "name": "Fortuner"
  },
  "category": {
    "id": 1,
    "name": "SUV",
    "icon": "/media/categories/icons/suv.png"
  },
  "features": [
    {
      "id": 1,
      "name": "Кондиционер"
    }
  ],
  "images": [
    {
      "id": 1,
      "image": "/media/cars/images/fortuner1.jpg"
    }
  ],
  "year": 2023,
  "color": "Белый",
  "transmission": "automatic",
  "oil_type": "petrol",
  "mileage": 15000,
  "status": "available"
}
```

### Bookings (Бронирования автомобилей)
- `GET /api/cars/bookings/` - Список всех бронирований
- `GET /api/cars/bookings/{id}/` - Детали конкретного бронирования

**Пример запроса POST:**
```json
{
  "car": 1,
  "telegram_id": "123456789",
  "client_name": "Иван Иванов",
  "client_phone": "+79991234567",
  "start_date": "2025-11-01",
  "end_date": "2025-11-07",
  "city": 1,
  "delivery_zone": 1,
  "provider_terms_accepted": true,
  "service_terms_accepted": true
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "car": {
    "id": 1,
    "title": "Toyota Fortuner 2023",
    "image": "/media/cars/images/fortuner1.jpg"
  },
  "telegram_id": "123456789",
  "client_name": "Иван Иванов",
  "client_phone": "+79991234567",
  "start_date": "2025-11-01",
  "end_date": "2025-11-07",
  "total_days": 7,
  "city": {
    "id": 1,
    "name": "Пхукет"
  },
  "delivery_zone": {
    "id": 1,
    "name": "Патонг",
    "price": 500.00
  },
  "rental_price": 14000.00,
  "delivery_price": 500.00,
  "deposit": 10000.00,
  "total_price": 24500.00,
  "status": "pending",
  "provider_terms_accepted": true,
  "service_terms_accepted": true,
  "provider_terms": "Условия прокатчика...",
  "created_at": "2025-10-26T10:00:00Z"
}
```

### Brands (Марки автомобилей)
- `GET /api/cars/brands/` - Список всех марок автомобилей

### Models (Модели автомобилей)
- `GET /api/cars/models/` - Список всех моделей
- `GET /api/cars/models/?brand_id=1` - Модели конкретной марки

### Categories (Категории автомобилей)
- `GET /api/cars/categories/` - Список всех категорий

### Features (Особенности автомобилей)
- `GET /api/cars/features/` - Список всех особенностей

### Cards (Карточки автомобилей)
- `GET /api/cars/cards/` - Все доступные автомобили в формате карточек

## 🏍️ Motorcycles API - Мотоциклы

### Motorcycles (Мотоциклы)
- `GET /api/motorcycles/motorcycles/` - Список всех мотоциклов
- `GET /api/motorcycles/motorcycles/{id}/` - Детали конкретного мотоцикла
**Структура данных аналогична Cars API**, включая:
- city
- rental_provider
- delivery_zones
- price_tiers (тарифы по дням)
- deposit

### Bookings (Бронирования мотоциклов)
- `GET /api/motorcycles/bookings/` - Список всех бронирований
- `GET /api/motorcycles/bookings/{id}/` - Детали конкретного бронирования

**Структура аналогична Cars Bookings**, включая:
- city
- delivery_zone
- rental_price
- delivery_price
- deposit
- provider_terms_accepted
- service_terms_accepted

### Остальные endpoints:
- `GET /api/motorcycles/brands/` - Марки мотоциклов
- `GET /api/motorcycles/models/` - Модели мотоциклов
- `GET /api/motorcycles/categories/` - Категории
- `GET /api/motorcycles/features/` - Особенности
- `GET /api/motorcycles/cards/` - Карточки
---

## 🏠 Houses API 

### Houses (Дома)
- `GET /api/houses/houses/` - Список всех домов
- `GET /api/houses/houses/{id}/` - Детали конкретного дома
- `POST /api/houses/houses/` - Создать новый дом (только админ)

**Структура данных аналогична Cars API**, включая:
- city
- rental_provider
- delivery_zones
- price_tiers (тарифы по дням)
- deposit

**Специфичные поля для домов:**
```json
{
  "area": 120.5,
  "bedrooms": 3,
  "bathrooms": 2,
  "floors": 2,
  "pool": true,
  "kitchen": true,
  "wifi": true
}
```

### Bookings (Бронирования домов)
- `GET /api/houses/bookings/` - Список всех бронирований
- `GET /api/houses/bookings/{id}/` - Детали конкретного бронирования
**Структура аналогична Cars Bookings**

### Остальные endpoints:
- `GET /api/houses/categories/` - Категории домов
- `GET /api/houses/features/` - Особенности
- `GET /api/houses/cards/` - Карточки
- `GET /api/houses/available/` - Доступные дома
- `GET /api/houses/availability/{id}/` - Проверка доступности
- `GET /api/houses/calendar/` - Календарь бронирований

---

## 🌴 Excursions API - Экскурсии

### Excursions (Экскурсии)
- `GET /api/excursions/excursions/` - Список всех экскурсий
- `GET /api/excursions/excursions/{id}/` - Детали конкретной экскурсии


**Пример ответа:**
```json
{
  "id": 1,
  "title": "Острова Пхи-Пхи",
  "description": "Незабываемая поездка на острова",
  "price_per_person": 1500.00,
  "deposit": 1000.00,
  "city": {
    "id": 1,
    "name": "Пхукет"
  },
  "rental_provider": {
    "id": 2,
    "name": "Phuket Tours",
    "phone": "+66987654321"
  },
  "delivery_zones": [
    {
      "id": 2,
      "name": "Карон",
      "price": 300.00
    }
  ],
  "price_tiers": [
    {
      "id": 1,
      "min_participants": 1,
      "price_per_person": 1500.00
    },
    {
      "id": 2,
      "min_participants": 4,
      "price_per_person": 1200.00
    },
    {
      "id": 3,
      "min_participants": 10,
      "price_per_person": 1000.00
    }
  ],
  "category": {
    "id": 1,
    "name": "Морские туры"
  },
  "features": [
    {
      "id": 1,
      "name": "Обед включен"
    }
  ],
  "images": [
    {
      "id": 1,
      "image": "/media/excursions/images/phi-phi.jpg"
    }
  ],
  "days": 1,
  "max_participants": 15,
  "status": "available"
}
```

### Bookings (Бронирования экскурсий)
- `GET /api/excursions/bookings/` - Список всех бронирований
- `GET /api/excursions/bookings/{id}/` - Детали конкретного бронирования

**Пример запроса POST:**
```json
{
  "excursion": 1,
  "telegram_id": "123456789",
  "client_name": "Иван Иванов",
  "client_phone": "+79991234567",
  "start_date": "2025-11-01",
  "end_date": "2025-11-01",
  "participants": 4,
  "city": 1,
  "delivery_zone": 2,
  "provider_terms_accepted": true,
  "service_terms_accepted": true
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "excursion": {
    "id": 1,
    "title": "Острова Пхи-Пхи",
    "image": "/media/excursions/images/phi-phi.jpg"
  },
  "telegram_id": "123456789",
  "client_name": "Иван Иванов",
  "client_phone": "+79991234567",
  "start_date": "2025-11-01",
  "end_date": "2025-11-01",
  "participants": 4,
  "total_days": 1,
  "city": {
    "id": 1,
    "name": "Пхукет"
  },
  "delivery_zone": {
    "id": 2,
    "name": "Карон",
    "price": 300.00
  },
  "excursion_price": 4800.00,
  "transfer_price": 300.00,
  "deposit": 1000.00,
  "total_price": 6100.00,
  "status": "pending",
  "provider_terms_accepted": true,
  "service_terms_accepted": true,
  "provider_terms": "Условия туроператора...",
  "created_at": "2025-10-26T10:00:00Z"
}
```

### Остальные endpoints:
- `GET /api/excursions/categories/` - Категории экскурсий
- `GET /api/excursions/features/` - Особенности
- `GET /api/excursions/cards/` - Карточки

---

## 📊 Статусы бронирований

Все бронирования (cars, motorcycles, houses, excursions) используют следующие статусы:

- `pending` - Ожидает подтверждения
- `confirmed` - Подтверждено
- `active` - Активно (в процессе)
- `completed` - Завершено
- `cancelled` - Отменено

## 💡 Важные особенности

### Расчет цены для Cars, Motorcycles, Houses:
Цена рассчитывается автоматически на основе `price_tiers`:
- Система выбирает подходящий тариф по количеству дней
- Пример: 7 дней * 2000 = 14000

### Расчет цены для Excursions:
Цена рассчитывается на основе количества участников:
- Система выбирает подходящий тариф по количеству участников
- Пример: 4 участника * 1200 = 4800

### Итоговая стоимость бронирования:
```
total_price = rental_price/excursion_price + delivery_price/transfer_price + deposit
```

### Обязательные поля при бронировании:
- `telegram_id` - ID пользователя Telegram
- `client_name` - Имя клиента
- `client_phone` - Телефон клиента
- `start_date` - Дата начала
- `end_date` - Дата окончания
- `city` - ID города
- `delivery_zone` - ID зоны доставки (опционально)
- `provider_terms_accepted` - Согласие с условиями прокатчика
- `service_terms_accepted` - Согласие с условиями сервиса
- `participants` - Количество участников (только для excursions)