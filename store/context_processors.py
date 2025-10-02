# store/context_processors.py
def ui_texts(request):
    lang = request.COOKIES.get('language', 'ru')
    translations = {
        'catalog': {'ru':'Каталог', 'en':'Catalog'},
        'settings': {'ru':'Настройки', 'en':'Settings'},
        'add_fav': {'ru':'Добавить в избранное', 'en':'Add to favorites'},
        'remove_fav': {'ru':'Убрать из избранного', 'en':'Remove from favorites'},
        'price': {'ru':'Цена', 'en':'Price'},
        'last_pages': {'ru':'Последние страницы', 'en':'Last pages'},
    }
    L = {k: v.get(lang, v.get('en')) for k, v in translations.items()}
    return {'L': L, 'LANG': lang}