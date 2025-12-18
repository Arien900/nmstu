from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from .models import User, Component, Build, BuildComponent


class ExportMixin:
    def export_to_xlsx(self, request, queryset):
        # Получаем выбранные поля из POST
        selected_model = request.POST.get('model')
        selected_fields = request.POST.getlist('fields')

        if not selected_model or not selected_fields:
            self.message_user(request, "Выберите модель и поля", level='ERROR')
            return

        # Динамически получаем модель по имени
        model_map = {
            'User': User,
            'Component': Component,
            'Build': Build,
            'BuildComponent': BuildComponent,
        }
        Model = model_map.get(selected_model)
        if not Model:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = selected_model

        # Заголовки
        ws.append(selected_fields)

        # Данные
        for obj in Model.objects.all():
            row = []
            for field in selected_fields:
                value = getattr(obj, field, '')
                if hasattr(value, '__call__'):
                    value = value()
                row.append(str(value))
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={selected_model}_export.xlsx'
        wb.save(response)
        return response

    export_to_xlsx.short_description = "Экспорт в XLSX"


@admin.register(User)
class UserAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('username', 'email', 'role', 'created_at')
    actions = ['export_to_xlsx']


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('name', 'category', 'price')
    actions = ['export_to_xlsx']


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('name', 'user', 'total_price', 'created_at')
    actions = ['export_to_xlsx']


@admin.register(BuildComponent)
class BuildComponentAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('build', 'component', 'quantity')
    actions = ['export_to_xlsx']