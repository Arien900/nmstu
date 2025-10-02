# store/data.py
PRODUCTS = [
    {
        "id": 1,
        "name": "Футболка 'Classic'",
        "description": "Хлопковая футболка — классический крой.",
        "styles": ["casual", "sport"],
        "sizes": ["S","M","L","XL"],
        "price": 799,
        "image": "images/tshirt1.jpg"
    },
    {
        "id": 2,
        "name": "Куртка 'Urban'",
        "description": "Тёплая куртка для прогулок в городе.",
        "styles": ["urban"],
        "sizes": ["M","L","XL","XXL"],
        "price": 3499,
        "image": "images/jacket1.jpg"
    },
    {
        "id": 3,
        "name": "Бэгги Джинсы",
        "description": "самые обхватывающие.",
        "styles": ["formal"],
        "sizes": ["M","L","XL"],
        "price": 5999,
        "image": "images/jeans1.jpg"
    },
]

# стиль теперь с метками на нескольких языках
STYLES = [
    {"code": "casual", "labels": {"ru": "Повседневный", "en": "Casual"}},
    {"code": "sport",  "labels": {"ru": "Спортивный", "en": "Sport"}},
    {"code": "urban",  "labels": {"ru": "Городской",  "en": "Urban"}},
    {"code": "formal", "labels": {"ru": "Формальный", "en": "Formal"}},
]

SIZES = ["XS","S","M","L","XL","XXL"]