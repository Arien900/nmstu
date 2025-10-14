import os
import uuid
from xml.etree import ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .forms import GradeForm, UploadFileForm

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_data(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            root = ET.Element("grade")
            for k, v in data.items():
                ET.SubElement(root, k).text = str(v)
            path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.xml")
            ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
            return HttpResponse("Сохранено!")
    return render(request, 'grades/form.html', {'form': GradeForm()})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            if not f.name.endswith('.xml'):
                return HttpResponse("Только .xml")
            path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.xml")
            with open(path, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            try:
                ET.parse(path)
                return HttpResponse("Загружено!")
            except:
                os.remove(path)
                return HttpResponse("Невалидный XML. Удалён.")
    return render(request, 'grades/upload.html', {'form': UploadFileForm()})

def list_files(request):
    files = []
    for name in os.listdir(UPLOAD_DIR):
        if name.endswith('.xml'):
            try:
                root = ET.parse(os.path.join(UPLOAD_DIR, name)).getroot()
                files.append({'name': name, 'data': {e.tag: e.text for e in root}})
            except:
                continue
    return render(request, 'grades/list.html', {
        'files': files or None,
        'error': 'Нет XML-файлов.' if not files else None
    })

def home(request):
    return list_files(request)

def export_file(request, filename):
    if not filename.endswith('.xml'):
        return HttpResponse("Только XML", status=400)
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        return HttpResponse("Файл не найден", status=404)
    with open(path, 'rb') as f:
        resp = HttpResponse(f.read(), content_type='application/xml')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

def export_all(request):
    root = ET.Element("grades")
    for name in os.listdir(UPLOAD_DIR):
        if name.endswith('.xml'):
            try:
                grade = ET.parse(os.path.join(UPLOAD_DIR, name)).getroot()
                root.append(grade)
            except:
                continue
    if len(root) == 0:
        return HttpResponse("Нет файлов", status=404)
    resp = HttpResponse(
        ET.tostring(root, encoding='utf-8', xml_declaration=True),
        content_type='application/xml'
    )
    resp['Content-Disposition'] = 'attachment; filename="all.xml"'
    return resp