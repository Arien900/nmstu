# pc/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
import openpyxl
from .forms import CustomUserCreationForm
from .models import Component, Build, BuildComponent, User, PresetBuild


def home_view(request):
    components = Component.objects.all().order_by('category', 'name')
    builds = []
    if request.user.is_authenticated and request.user.role != 'guest':
        builds = request.user.builds.all()
    return render(request, 'pc/home.html', {
        'components': components,
        'builds': builds,
        'user_role': request.user.role if request.user.is_authenticated else 'guest'
    })


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'pc/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Привет, {user.username}!")
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'pc/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли.")
    return redirect('home')


def presets_view(request):
    presets = PresetBuild.objects.all()
    return render(request, 'pc/presets.html', {'presets': presets})


@login_required
def use_preset_view(request, preset_id):
    preset = get_object_or_404(PresetBuild, id=preset_id)
    components = preset.get_components()
    if not components:
        messages.error(request, "Нет компонентов для этой сборки. Добавьте их через админку.")
        return redirect('presets')

    build = Build.objects.create(
        user=request.user,
        name=f"Моя {preset.name}",
        total_price=sum(c.price for c in components)
    )
    for comp in components:
        BuildComponent.objects.create(build=build, component=comp, quantity=1)
    messages.success(request, f"Сборка «{build.name}» создана!")
    return redirect('home')


@login_required
def create_build_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        component_ids = request.POST.getlist("components")
        if not name:
            messages.error(request, "Укажите название сборки.")
            return render(request, 'pc/create_build.html', {
                'components': Component.objects.all(),
                'selected_ids': component_ids
            })

        if not component_ids:
            messages.error(request, "Выберите хотя бы один компонент.")
            return render(request, 'pc/create_build.html', {
                'components': Component.objects.all(),
                'selected_ids': component_ids
            })

        selected = Component.objects.filter(id__in=component_ids)
        component_list = list(selected)

        # Проверка совместимости
        errors = []
        for i, comp1 in enumerate(component_list):
            for comp2 in component_list[i+1:]:
                if not comp1.is_compatible_with(comp2):
                    errors.append(f"❌ {comp1.name} несовместим с {comp2.name}")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'pc/create_build.html', {
                'components': Component.objects.all(),
                'selected_ids': component_ids
            })

        # Создаём сборку
        build = Build.objects.create(user=request.user, name=name)
        total = sum(comp.price for comp in component_list)
        build.total_price = total
        build.save()

        for comp in component_list:
            BuildComponent.objects.create(build=build, component=comp, quantity=1)

        messages.success(request, f"Сборка «{name}» создана!")
        return redirect('home')

    return render(request, 'pc/create_build.html', {
        'components': Component.objects.all(),
    })


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def export_view(request):
    if request.method == "POST":
        model_name = request.POST.get("model")
        fields = request.POST.getlist("fields")

        model_map = {
            "Component": Component,
            "Build": Build,
            "BuildComponent": BuildComponent,
            "User": User,
            "PresetBuild": PresetBuild,
        }
        Model = model_map.get(model_name)
        if not Model or not fields:
            messages.error(request, "Выберите модель и поля.")
            return redirect('export')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = model_name
        ws.append(fields)

        for obj in Model.objects.all():
            row = []
            for field in fields:
                try:
                    value = getattr(obj, field)
                    if callable(value):
                        value = value()
                    row.append(str(value))
                except AttributeError:
                    row.append("")
            ws.append(row)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="{model_name}_export.xlsx"'
        wb.save(response)
        return response

    models_info = [
        {"name": "Component", "fields": ["id", "name", "category", "price", "socket", "ram_type"]},
        {"name": "Build", "fields": ["id", "name", "user", "total_price"]},
        {"name": "BuildComponent", "fields": ["id", "build", "component", "quantity"]},
        {"name": "User", "fields": ["id", "username", "email", "role"]},
        {"name": "PresetBuild", "fields": ["id", "name", "target"]},
    ]
    return render(request, "pc/export.html", {"models": models_info})