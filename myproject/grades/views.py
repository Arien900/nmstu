import os
import uuid
from xml.etree import ElementTree as ET
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError, models
from django.views.decorators.http import require_http_methods
from .forms import GradeForm, UploadFileForm
from .models import GradeRecord

UPLOAD_DIR = os.path.join('media', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
                root = ET.Element("grade")
                for k in ['student', 'subject', 'grade']:
                    ET.SubElement(root, k).text = str(data[k])
                path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.xml")
                ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
                return redirect('home')
    else:
        form = GradeForm()
    return render(request, 'grades/form.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            if not f.name.endswith('.xml'):
                form.add_error('file', 'Только XML-файлы!')
            else:
                path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.xml")
                with open(path, 'wb') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
                try:
                    ET.parse(path)
                    return redirect('home')
                except:
                    os.remove(path)
                    form.add_error('file', 'Невалидный XML!')
    else:
        form = UploadFileForm()
    return render(request, 'grades/upload.html', {'form': form})

def list_files(request):
    source = request.GET.get('source', 'db')
    context = {'source': source}
    if source == 'file':
        files = []
        for name in os.listdir(UPLOAD_DIR):
            if name.endswith('.xml'):
                try:
                    root = ET.parse(os.path.join(UPLOAD_DIR, name)).getroot()
                    files.append({e.tag: e.text for e in root})
                except:
                    continue
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
        student = request.POST.get('student', '').strip()
        subject = request.POST.get('subject', '').strip()
        grade_str = request.POST.get('grade', '').strip()
        if not student or not subject or not grade_str:
            return JsonResponse({'error': 'Все поля обязательны'}, status=400)
        try:
            grade = int(grade_str)
            if grade < 1 or grade > 5:
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'Оценка от 1 до 5'}, status=400)
        record = GradeRecord.objects.get(pk=pk)
        record.student = student
        record.subject = subject
        record.grade = grade
        record.save()
        return JsonResponse({'ok': True})
    except GradeRecord.DoesNotExist:
        return JsonResponse({'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
def delete_record(request, pk):
    try:
        GradeRecord.objects.get(pk=pk).delete()
        return JsonResponse({'ok': True})
    except:
        return JsonResponse({'error': 'Запись не найдена'}, status=404)