import os
from xml.etree import ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .forms import GradeForm, UploadFileForm

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAIN_XML = os.path.join(UPLOAD_DIR, 'grades.xml')

def ensure_main_xml():
    if not os.path.exists(MAIN_XML):
        root = ET.Element("grades")
        ET.ElementTree(root).write(MAIN_XML, encoding='utf-8', xml_declaration=True)

def save_data(request):
    ensure_main_xml()
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            tree = ET.parse(MAIN_XML)
            root = tree.getroot()
            grade_elem = ET.SubElement(root, "grade")
            for k, v in form.cleaned_data.items():
                ET.SubElement(grade_elem, k).text = str(v)
            tree.write(MAIN_XML, encoding='utf-8', xml_declaration=True)
            return HttpResponse("Добавлено в общий XML!")
    return render(request, 'grades/form.html', {'form': GradeForm()})

def upload_file(request):
    ensure_main_xml()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            if not f.name.endswith('.xml'):
                return HttpResponse("Только .xml")
            temp_path = os.path.join(UPLOAD_DIR, 'temp.xml')
            with open(temp_path, 'wb') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            try:
                temp_tree = ET.parse(temp_path)
                temp_root = temp_tree.getroot()
                main_tree = ET.parse(MAIN_XML)
                main_root = main_tree.getroot()
                for grade in temp_root.findall('grade'):
                    main_root.append(grade)
                main_tree.write(MAIN_XML, encoding='utf-8', xml_declaration=True)
                os.remove(temp_path)
                return HttpResponse("Записи добавлены в общий XML!")
            except Exception as e:
                os.remove(temp_path)
                return HttpResponse(f"Ошибка XML: {e}")
    return render(request, 'grades/upload.html', {'form': UploadFileForm()})

def list_files(request):
    ensure_main_xml()
    try:
        root = ET.parse(MAIN_XML).getroot()
        files = []
        for i, grade in enumerate(root.findall('grade')):
            data = {child.tag: child.text for child in grade}
            files.append({'name': f'Запись #{i+1}', 'data': data})
        return render(request, 'grades/list.html', {'files': files})
    except:
        return render(request, 'grades/list.html', {'files': None})

def export_all(request):
    ensure_main_xml()
    if not os.path.exists(MAIN_XML):
        return HttpResponse("Нет данных", status=404)
    with open(MAIN_XML, 'rb') as f:
        resp = HttpResponse(f.read(), content_type='application/xml')
        resp['Content-Disposition'] = 'attachment; filename="grades.xml"'
        return resp