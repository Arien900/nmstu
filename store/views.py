from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .data import PRODUCTS, STYLES, SIZES
from .forms import SettingsForm
import json

# Вспомогалки
def get_product(product_id):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return None

def index(request):
    products = PRODUCTS.copy()
    # Читаем cookie избранных (список id)
    fav_cookie = request.COOKIES.get('favorites')
    favorites = []
    if fav_cookie:
        try:
            favorites = json.loads(fav_cookie)
        except:
            favorites = []
    # читаем последнее посещение
    last_pages = request.COOKIES.get('last_pages')
    last_pages = json.loads(last_pages) if last_pages else []
    context = {
        'products': products,
        'favorites': favorites,
        'styles': STYLES,
        'sizes': SIZES,
        'last_pages': last_pages,
    }
    response = render(request, 'store/index.html', context)
    # Также можно обновить cookie last_pages: добавляем главную
    # Но делаем это в middleware-like вручную: получим last_pages, добавляем текущий путь:
    try:
        lp = list(last_pages)
    except:
        lp = []
    if '/' not in lp:
        lp.insert(0, '/')
        lp = lp[:5]  # храним максимум 5
    response.set_cookie('last_pages', json.dumps(lp), max_age=60*60*24*30)  # 30 дней
    return response

def product_detail(request, product_id):
    product = get_product(product_id)
    if not product:
        return HttpResponse("Product not found", status=404)
    # Установим last_pages cookie: добавляем текущую страницу в начало
    last_pages_cookie = request.COOKIES.get('last_pages')
    last_pages = json.loads(last_pages_cookie) if last_pages_cookie else []
    current = f'/product/{product_id}/'
    if current in last_pages:
        last_pages.remove(current)
    last_pages.insert(0, current)
    last_pages = last_pages[:5]

    # favorites
    fav_cookie = request.COOKIES.get('favorites')
    favorites = json.loads(fav_cookie) if fav_cookie else []

    context = {
        'product': product,
        'favorites': favorites,
        'styles': STYLES,
    }
    response = render(request, 'store/product_detail.html', context)
    response.set_cookie('last_pages', json.dumps(last_pages), max_age=60*60*24*30)
    return response

def user_settings(request):
    # Обработка формы настроек — сохраняем в cookies
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            theme = form.cleaned_data.get('theme', 'light') or 'light'
            language = form.cleaned_data.get('language', 'en') or 'en'
            favorite_styles = form.cleaned_data.get('favorite_styles') or []
            preferred_sizes = form.cleaned_data.get('preferred_sizes') or []

            response = redirect('store:index')
            response.set_cookie('theme', theme, max_age=60*60*24*365)  # 1 год
            response.set_cookie('language', language, max_age=60*60*24*365)
            response.set_cookie('favorite_styles', json.dumps(favorite_styles), max_age=60*60*24*365)
            response.set_cookie('preferred_sizes', json.dumps(preferred_sizes), max_age=60*60*24*365)
            return response
    else:
        # начальные значения из cookie
        initial = {}
        initial['theme'] = request.COOKIES.get('theme', 'light')
        initial['language'] = request.COOKIES.get('language', 'ru')
        fs = request.COOKIES.get('favorite_styles')
        ps = request.COOKIES.get('preferred_sizes')
        try:
            initial['favorite_styles'] = json.loads(fs) if fs else []
        except:
            initial['favorite_styles'] = []
        try:
            initial['preferred_sizes'] = json.loads(ps) if ps else []
        except:
            initial['preferred_sizes'] = []
        form = SettingsForm(initial=initial)
    return render(request, 'store/settings.html', {'form': form, 'styles': STYLES, 'sizes': SIZES})

from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def toggle_favorite(request, product_id):
    import json
    fav_cookie = request.COOKIES.get('favorites')
    try:
        favorites = json.loads(fav_cookie) if fav_cookie else []
    except:
        favorites = []
    if product_id in favorites:
        favorites.remove(product_id)
        action = 'removed'
    else:
        favorites.append(product_id)
        action = 'added'
    response = JsonResponse({'status': 'ok', 'action': action, 'favorites': favorites})
    response.set_cookie('favorites', json.dumps(favorites), max_age=60*60*24*30)
    return response