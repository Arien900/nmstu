# store/data.py

PRODUCTS = [
    {
        "id": 1,
        "name": "Футболка 'Classic'",
        "description": "Хлопковая футболка — классический крой.",
        "styles": ["casual", "sport"],
        "sizes": ["S", "M", "L", "XL"],
        "price": 799,
        "image": "images/tshirt1.jpg",
    },
    {
        "id": 2,
        "name": "Джинсы 'Denim'",
        "description": "Удобные прямые джинсы.",
        "styles": ["casual"],
        "sizes": ["M", "L", "XL"],
        "price": 2499,
        "image": "images/jeans1.jpg",
    },
    {
        "id": 3,
        "name": "Куртка 'Urban'",
        "description": "Лёгкая куртка для весны/осени.",
        "styles": ["urban", "casual"],
        "sizes": ["M", "L"],
        "price": 4999,
        "image": "images/jacket1.jpg",
    },
    # добавь ещё элементы по желанию
]

STYLES = [
    {"code": "casual", "label": "Casual"},
    {"code": "sport", "label": "Sport"},
    {"code": "urban", "label": "Urban"},
    {"code": "formal", "label": "Formal"},
]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]