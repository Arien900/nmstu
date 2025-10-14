import os
import json
import uuid
from xml.etree import ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .forms import GradeForm, UploadFileForm
from django.http import HttpResponse
import json
import xml.etree.ElementTree as ET

def export_file(request, filename):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path) or not filename.endswith(('.json', '.xml')):
        return HttpResponse("Файл не найден.", status=404)
    
    with open(path, 'rb') as f:
        content = f.read()
    
    response = HttpResponse(content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_data(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            fmt = request.POST.get('format')
            filename = f"{uuid.uuid4()}.{fmt}"
            path = os.path.join(UPLOAD_DIR, filename)
            if fmt == 'json':
                with open(path, 'w') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif fmt == 'xml':
                root = ET.Element("grade")
                for k, v in data.items():
                    ET.SubElement(root, k).text = str(v)
                tree = ET.ElementTree(root)
                tree.write(path, encoding='utf-8', xml_declaration=True)
            return HttpResponse("Сохранено!")
    else:
        form = GradeForm()
    return render(request, 'grades/form.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            ext = f.name.split('.')[-1].lower()
            if ext not in ('json', 'xml'):
                return HttpResponse("Неверный формат файла.")
            safe_name = f"{uuid.uuid4()}.{ext}"
            path = os.path.join(UPLOAD_DIR, safe_name)
            with open(path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            try:
                if ext == 'json':
                    with open(path) as fd:
                        json.load(fd)
                else:
                    ET.parse(path)
            except Exception:
                os.remove(path)
                return HttpResponse("Невалидный файл. Удалён.")
            return HttpResponse("Файл загружен и проверен.")
    else:
        form = UploadFileForm()
    return render(request, 'grades/upload.html', {'form': form})

def list_files(request):
    files = []
    for fname in os.listdir(UPLOAD_DIR):
        if fname.endswith(('.json', '.xml')):
            path = os.path.join(UPLOAD_DIR, fname)
            try:
                if fname.endswith('.json'):
                    with open(path) as f:
                        content = json.load(f)
                else:
                    tree = ET.parse(path)
                    root = tree.getroot()
                    content = {child.tag: child.text for child in root}
                files.append({'name': fname, 'data': content})
            except Exception:
                continue
    context = {'files': files} if files else {'error': 'Нет файлов.'}
    return render(request, 'grades/list.html', context)
def home(request):
    return list_files(request)
def export_combined(request, ext):
    if ext not in ('json', 'xml'):
        return HttpResponse("Неверный формат.", status=400)
    
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(f'.{ext}')]
    if not files:
        return HttpResponse(f"Нет файлов формата .{ext}.", status=404)

    if ext == 'json':
        data = []
        for fname in files:
            try:
                with open(os.path.join(UPLOAD_DIR, fname), encoding='utf-8') as f:
                    data.append(json.load(f))
            except Exception:
                continue
        content = json.dumps(data, ensure_ascii=False, indent=2)
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="all_grades.json"'

    else:  # xml
        root = ET.Element("grades")
        for fname in files:
            try:
                tree = ET.parse(os.path.join(UPLOAD_DIR, fname))
                grade_elem = tree.getroot()
                root.append(grade_elem)
            except Exception:
                continue
        content = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        response = HttpResponse(content, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="all_grades.xml"'

    return response