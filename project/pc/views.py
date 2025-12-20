from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Component, Build, BuildComponent, User
import openpyxl
from django.http import HttpResponse
from django.db import models

# Главная страница
def home_view(request):
    comps = Component.objects.all()
    builds = request.user.builds.all() if request.user.is_authenticated else []
    return render(request, 'pc/home.html', {'comps': comps, 'builds': builds})


# Регистрация
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "✅ Регистрация успешна!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'pc/register.html', {'form': form})


# Вход
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            messages.error(request, "❌ Укажите логин и пароль.")
            return redirect('login')  # ← render → redirect
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"✅ Добро пожаловать, {user.username}!")
            return redirect('home')
        messages.error(request, "❌ Неверный логин или пароль.")
    return render(request, 'pc/login.html')


# Выход
def logout_view(request):
    logout(request)
    messages.info(request, "✅ Вы вышли.")
    return redirect('home')


# Готовые сборки — ИСПРАВЛЕНО: 'Core i5', 'Ryzen 5'
def presets_view(request):
    presets_data = [
        {
            'name': '🎮 Игровая 2025',
            'target': 'gaming',
            'description': 'Для игр в 1440p',
            'keywords': ['Core i5', 'B760', 'DDR5', 'RTX', '32ГБ', '980', 'RM850', 'AK620'],
        },
        {
            'name': '💼 Офисная',
            'target': 'office',
            'description': 'Для Zoom и Excel',
            'keywords': ['Ryzen 5', 'B650', 'DDR5', '970', 'MWE 550']
        }
    ]
    
    result = []
    for preset in presets_data:
        from django.db.models import Q
        q = Q()
        for kw in preset['keywords']:
            q |= Q(name__icontains=kw)
        components = Component.objects.filter(q)
        total = sum(c.price for c in components)
        result.append({
            'preset': preset,
            'components': components,  # ← единообразно 'components'
            'total': total
        })
    return render(request, 'pc/presets.html', {'presets': result})


# Использовать пресет
@login_required
def use_preset_view(request, pid):
    presets = {
        1: {'name': 'Игровая 2025', 'keywords': ['Core i5', 'B760', 'DDR5', 'RTX']},
        2: {'name': 'Офисная', 'keywords': ['Ryzen 5', 'B650', 'DDR5']},
    }
    if pid not in presets:
        messages.error(request, "❌ Пресет не найден.")
        return redirect('presets')

    from django.db.models import Q
    q = Q()
    for kw in presets[pid]['keywords']:
        q |= Q(name__icontains=kw)
    components = Component.objects.filter(q)

    if not components:
        messages.error(request, "⚠️ Нет подходящих компонентов.")
        return redirect('presets')

    try:
        build = Build.objects.create(
            user=request.user,
            name=presets[pid]['name'],
            total_price=sum(c.price for c in components)
        )
        for c in components:
            BuildComponent.objects.create(build=build, component=c)
        messages.success(request, f"✅ «{presets[pid]['name']}» создана!")
        return redirect('build', build.id)
    except:
        messages.error(request, "❌ Сборка с таким именем уже есть.")
        return redirect('presets')


# Создать сборку — ИСПРАВЛЕНО: все render → redirect при ошибках
@login_required
def create_build(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        ids = request.POST.getlist("components")
        if not name or not ids:
            messages.error(request, "❌ Укажите название и компоненты.")
            return redirect('create_build')  # ← render → redirect

        try:
            ids = [int(i) for i in ids]
            selected = list(Component.objects.filter(id__in=ids))
        except:
            messages.error(request, "❌ Некорректные ID.")
            return redirect('create_build')  # ← render → redirect

        for i, c1 in enumerate(selected):
            for c2 in selected[i+1:]:
                if not c1.is_compatible_with(c2):
                    messages.error(request, f"❌ {c1.name} несовместим с {c2.name}")
                    return redirect('create_build')  # ← render → redirect

        try:
            build = Build.objects.create(
                user=request.user,
                name=name,
                total_price=sum(c.price for c in selected)
            )
            for c in selected:
                BuildComponent.objects.create(build=build, component=c)
            messages.success(request, f"✅ «{name}» создана!")
            return redirect('build', build.id)
        except:
            messages.error(request, "❌ Сборка с таким именем уже есть.")
            return redirect('create_build')  # ← render → redirect

    return render(request, 'pc/create_build.html', {
        'components': Component.objects.all()
    })


# Детали сборки
@login_required
def build_detail(request, bid):
    build = get_object_or_404(Build, id=bid, user=request.user)
    components = build.components.select_related('component')
    return render(request, 'pc/build_detail.html', {
        'build': build,
        'components': components
    })


# Проверка: админ?
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# Админка
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Статистика
    total_price = Build.objects.aggregate(total=models.Sum('total_price'))['total'] or 0
    builds_count = Build.objects.count()
    
    stats = {
        'users': User.objects.count(),
        'comps': Component.objects.count(),
        'builds': builds_count,
        'total_price': total_price,
        'avg_price': round(total_price / builds_count, 0) if builds_count else 0,
    }

    # Последние 5 сборок
    recent_builds = Build.objects.select_related('user').order_by('-created_at')[:5]

    return render(request, 'pc/admin/dashboard.html', {
        'stats': stats,
        'recent_builds': recent_builds,
    })


# Экспорт в XLSX
@login_required
@user_passes_test(is_admin)
def export_data(request):
    if request.method == "POST":
        model_name = request.POST.get("model", "Component")
        fields = request.POST.getlist("f") or ["id", "name", "price"]
        Model = {"Component": Component, "Build": Build, "User": User}.get(model_name, Component)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(fields)
        for obj in Model.objects.all():
            ws.append([str(getattr(obj, f, "")) for f in fields])

        res = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        res["Content-Disposition"] = f'attachment; filename="{model_name}.xlsx"'
        wb.save(res)
        return res

    return render(request, "pc/export.html", {"models": ["Component", "Build", "User"]})


# Удаление сборки
@login_required
def delete_build_view(request, build_id):
    build = get_object_or_404(Build, id=build_id, user=request.user)
    if request.method == "POST":
        build.delete()
        messages.success(request, "🗑️ Сборка удалена.")
        return redirect('home')
    return redirect('build', build_id=build.id)

@login_required
def edit_build(request, bid):
    build = get_object_or_404(Build, id=bid, user=request.user)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        ids = request.POST.getlist("components")
        if not name or not ids:
            messages.error(request, "❌ Укажите название и компоненты.")
            return redirect('edit_build', bid=bid)

        try:
            ids = [int(i) for i in ids]
            selected = list(Component.objects.filter(id__in=ids))
        except:
            messages.error(request, "❌ Некорректные ID.")
            return redirect('edit_build', bid=bid)

        for i, c1 in enumerate(selected):
            for c2 in selected[i+1:]:
                if not c1.is_compatible_with(c2):
                    messages.error(request, f"❌ {c1.name} несовместим с {c2.name}")
                    return redirect('edit_build', bid=bid)

        # Обновляем сборку
        build.name = name
        build.total_price = sum(c.price for c in selected)
        build.save()

        # Обновляем компоненты
        build.components.all().delete()
        for c in selected:
            BuildComponent.objects.create(build=build, component=c)

        messages.success(request, f"✅ «{name}» обновлена!")
        return redirect('build', bid=build.id)

    #показываем текущие компоненты
    selected_ids = [bc.component.id for bc in build.components.all()]
    return render(request, 'pc/create_build.html', {
        'build': build,
        'components': Component.objects.all(),
        'selected_ids': selected_ids
    })

@login_required
@user_passes_test(is_admin)
def admin_add_component(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "").strip()
        price = request.POST.get("price", "0")
        socket = request.POST.get("socket", "").strip()
        ram_type = request.POST.get("ram_type", "").strip()
        has_pcie = request.POST.get("has_pcie") == "on"

        if not name or not category:
            messages.error(request, "❌ Укажите название и категорию.")
        else:
            try:
                Component.objects.create(
                    name=name,
                    category=category,
                    price=int(price),
                    socket=socket,
                    ram_type=ram_type,
                    has_pcie=has_pcie
                )
                messages.success(request, f"✅ «{name}» добавлен!")
                return redirect('admin_dashboard')
            except ValueError:
                messages.error(request, "❌ Цена должна быть числом.")

    return render(request, 'pc/admin/add_component.html')


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'pc/admin/users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_export_xlsx(request):
    if request.method != "POST":
        return render(request, 'pc/admin/export.html')

    model_name = request.POST.get("model")
    Model = {
        "Component": Component,
        "User": User,
        "Build": Build,
    }.get(model_name)

    if not Model:
        messages.error(request, "❌ Неверная модель.")
        return redirect('admin_export_xlsx')

    # Формируем XLSX
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = model_name

    # Заголовки
    if model_name == "Component":
        headers = ["ID", "Название", "Категория", "Цена", "Сокет", "Тип ОЗУ", "PCIe"]
        ws.append(headers)
        for obj in Model.objects.all():
            ws.append([
                obj.id,
                obj.name,
                obj.category,
                obj.price,
                obj.socket,
                obj.ram_type,
                "Да" if obj.has_pcie else "Нет"
            ])
    elif model_name == "User":
        headers = ["ID", "Логин", "Роль", "Email", "Дата регистрации"]
        ws.append(headers)
        for obj in Model.objects.all():
            ws.append([
                obj.id,
                obj.username,
                obj.get_role_display(),
                obj.email or "-",
                obj.date_joined.strftime("%d.%m.%Y %H:%M")
            ])
    elif model_name == "Build":
        headers = ["ID", "Пользователь", "Название", "Цена", "Компонентов", "Дата"]
        ws.append(headers)
        for obj in Model.objects.select_related('user').prefetch_related('components'):
            comps = obj.components.count()
            ws.append([
                obj.id,
                obj.user.username,
                obj.name,
                obj.total_price,
                comps,
                obj.created_at.strftime("%d.%m.%Y %H:%M")
            ])

    # Отправка
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{model_name}_export.xlsx"'
    wb.save(response)
    return response