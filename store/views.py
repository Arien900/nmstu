# store/views.py (фрагменты)
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .data import PRODUCTS, STYLES, SIZES
from .forms import SettingsForm
import json

def _read_favorites_from_cookie(cookie_value):
    if not cookie_value:
        return []
    try:
        arr = json.loads(cookie_value)
        # привести к int (на случай, если строки)
        return [int(x) for x in arr]
    except:
        return []

def index(request):
    products = list(PRODUCTS)  # shallow copy
    # favorites — гарантированно list[int]
    favorites = _read_favorites_from_cookie(request.COOKIES.get('favorites'))

    # preferred filters из cookie (сохранены как коды стилей / размеры)
    favorite_styles = []
    try:
        favorite_styles = json.loads(request.COOKIES.get('favorite_styles') or '[]')
    except:
        favorite_styles = []

    preferred_sizes = []
    try:
        preferred_sizes = json.loads(request.COOKIES.get('preferred_sizes') or '[]')
    except:
        preferred_sizes = []

    # Поддерживаем фильтрацию через GET: ?style=casual&size=M
    style_q = request.GET.get('style')
    size_q = request.GET.get('size')
    if style_q:
        products = [p for p in products if style_q in p.get('styles', [])]
    if size_q:
        products = [p for p in products if size_q in p.get('sizes', [])]

    # Пример: фильтр "показывать по предпочтениям" ?filter=preferred
    if request.GET.get('filter') == 'preferred' and favorite_styles:
        products = [p for p in products if any(s in favorite_styles for s in p.get('styles', []))]

    # last pages
    last_pages = []
    try:
        last_pages = json.loads(request.COOKIES.get('last_pages') or '[]')
    except:
        last_pages = []

    context = {
        'products': products,
        'favorites': favorites,
        'styles': STYLES,
        'sizes': SIZES,
        'last_pages': last_pages,
    }
    response = render(request, 'store/index.html', context)
    # Обновим last_pages cookie — добавляем текущую страницу
    lp = list(last_pages)
    current = '/'
    if current in lp:
        lp.remove(current)
    lp.insert(0, current)
    lp = lp[:5]
    response.set_cookie('last_pages', json.dumps(lp), max_age=60*60*24*30)
    return response

def product_detail(request, product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return HttpResponse('Not found', status=404)

    # favorites
    favorites = _read_favorites_from_cookie(request.COOKIES.get('favorites'))

    # last pages
    last_pages = []
    try:
        last_pages = json.loads(request.COOKIES.get('last_pages') or '[]')
    except:
        last_pages = []
    current = f'/product/{product_id}/'
    if current in last_pages:
        last_pages.remove(current)
    last_pages.insert(0, current)
    last_pages = last_pages[:5]

    context = {'product': product, 'favorites': favorites, 'styles': STYLES}
    response = render(request, 'store/product_detail.html', context)
    response.set_cookie('last_pages', json.dumps(last_pages), max_age=60*60*24*30)
    return response

from django.views.decorators.http import require_http_methods
@require_http_methods(['POST'])
def toggle_favorite(request, product_id):
    fav_cookie = request.COOKIES.get('favorites')
    favorites = _read_favorites_from_cookie(fav_cookie)

    if product_id in favorites:
        favorites.remove(product_id)
        action = 'removed'
    else:
        favorites.append(product_id)
        action = 'added'

    response = JsonResponse({'status': 'ok', 'action': action, 'favorites': favorites})
    response.set_cookie('favorites', json.dumps(favorites), max_age=60*60*24*30)
    return response

def user_settings(request):
    lang = request.COOKIES.get('language', 'ru')
    if request.method == 'POST':
        form = SettingsForm(request.POST, lang=lang)
        if form.is_valid():
            theme = form.cleaned_data.get('theme', 'light') or 'light'
            language = form.cleaned_data.get('language', 'ru') or 'ru'
            favorite_styles = form.cleaned_data.get('favorite_styles') or []
            preferred_sizes = form.cleaned_data.get('preferred_sizes') or []

            response = redirect('store:index')
            response.set_cookie('theme', theme, max_age=60*60*24*365)
            response.set_cookie('language', language, max_age=60*60*24*365)
            response.set_cookie('favorite_styles', json.dumps(favorite_styles), max_age=60*60*24*365)
            response.set_cookie('preferred_sizes', json.dumps(preferred_sizes), max_age=60*60*24*365)
            return response
    else:
        initial = {}
        initial['theme'] = request.COOKIES.get('theme', 'light')
        initial['language'] = request.COOKIES.get('language', 'ru')
        try:
            initial['favorite_styles'] = json.loads(request.COOKIES.get('favorite_styles') or '[]')
        except:
            initial['favorite_styles'] = []
        try:
            initial['preferred_sizes'] = json.loads(request.COOKIES.get('preferred_sizes') or '[]')
        except:
            initial['preferred_sizes'] = []
        form = SettingsForm(initial=initial, lang=lang)

    return render(request, 'store/settings.html', {'form': form})