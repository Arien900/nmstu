import os
from xml.etree import ElementTree as ET
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError, models
from django.views.decorators.http import require_http_methods
from .forms import GradeForm, UploadFileForm
from .models import GradeRecord

UPLOAD_DIR = os.path.join('media', 'uploads')
MAIN_XML = os.path.join(UPLOAD_DIR, 'grades.xml')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def ensure_main_xml():
    if not os.path.exists(MAIN_XML):
        root = ET.Element("grades")
        ET.ElementTree(root).write(MAIN_XML, encoding='utf-8', xml_declaration=True)

def save_data(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['save_to'] == 'db':
                try:
                    GradeRecord.objects.create(
                        student=data['student'],
                        subject=data['subject'],
                        grade=data['grade']
                    )
                    return redirect('home')
                except IntegrityError:
                    form.add_error(None, "Такая запись уже есть в базе!")
            else:
                ensure_main_xml()
                tree = ET.parse(MAIN_XML)
                root = tree.getroot()
                grade_elem = ET.SubElement(root, "grade")
                for k in ['student', 'subject', 'grade']:
                    ET.SubElement(grade_elem, k).text = str(data[k])
                tree.write(MAIN_XML, encoding='utf-8', xml_declaration=True)
                return redirect('home')
    else:
        form = GradeForm()
    return render(request, 'grades/form.html', {'form': form})

def upload_file(request):
    ensure_main_xml()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            if not f.name.endswith('.xml'):
                form.add_error('file', 'Только XML-файлы!')
            else:
                temp_path = os.path.join(UPLOAD_DIR, 'temp.xml')
                with open(temp_path, 'wb') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
                try:
                    temp_tree = ET.parse(temp_path)
                    main_tree = ET.parse(MAIN_XML)
                    main_root = main_tree.getroot()
                    for grade in temp_tree.findall('grade'):
                        main_root.append(grade)
                    main_tree.write(MAIN_XML, encoding='utf-8', xml_declaration=True)
                    os.remove(temp_path)
                    return redirect('home')
                except Exception:
                    os.remove(temp_path)
                    form.add_error('file', 'Невалидный XML!')
    else:
        form = UploadFileForm()
    return render(request, 'grades/upload.html', {'form': form})

def list_files(request):
    source = request.GET.get('source', 'db')
    context = {'source': source}
    if source == 'file':
        files = []
        if os.path.exists(MAIN_XML):
            try:
                root = ET.parse(MAIN_XML).getroot()
                for grade in root.findall('grade'):
                    files.append({child.tag: child.text for child in grade})
            except:
                pass
        context['files'] = files
    else:
        context['records'] = GradeRecord.objects.all()
    return render(request, 'grades/list.html', context)
def search_records(request):
    query = request.GET.get('q', '')
    records = GradeRecord.objects.filter(
        models.Q(student__icontains=query) | models.Q(subject__icontains=query)
    ) if query else GradeRecord.objects.all()
    return JsonResponse([{'id': r.id, 'student': r.student, 'subject': r.subject, 'grade': r.grade} for r in records], safe=False)

@require_http_methods(["POST"])
def edit_record(request, pk):
    try:
        r = GradeRecord.objects.get(pk=pk)
        s, subj, g = request.POST.get('student'), request.POST.get('subject'), request.POST.get('grade')
        if not s or not subj or not g:
            return JsonResponse({'error': 'Все поля обязательны'}, status=400)
        g = int(g)
        if g < 1 or g > 5:
            return JsonResponse({'error': 'Оценка от 1 до 5'}, status=400)
        r.student, r.subject, r.grade = s, subj, g
        r.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
def delete_record(request, pk):
    try:
        GradeRecord.objects.get(pk=pk).delete()
        return JsonResponse({'ok': True})
    except:
        return JsonResponse({'error': 'Запись не найдена'}, status=404)
