from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Floor, Polygon
import json

def map(request):
    floors = Floor.objects.all().order_by('number')
    first_floor = floors.first()
    context = {
        'initial_floor': first_floor.number if first_floor else 1,
        'total_floors': floors.count(),
        'floors': floors,
    }
    return render(request, 'index.html', context)

def admin_map(request):
    floors = Floor.objects.all()
    context = {
        'floors': floors,
        'initial_floor': floors.first().number if floors.exists() else 1,
        'total_floors': floors.count()
    }
    return render(request, 'admin_map.html', context)

def get_polygons(request, floor_number):
    floor = Floor.objects.filter(number=floor_number).first()
    if not floor:
        return JsonResponse({'error': 'Этаж не найден'}, status=404)
    
    polygons = floor.polygons.all()
    polygon_data = [
        {
            'description': polygon.description,
            'short_description': polygon.short_description,
            'coordinates': polygon.coordinates
        }
        for polygon in polygons
    ]
    return JsonResponse({'polygons': polygon_data, 'svg_path': floor.svg_path})

@csrf_exempt
def add_polygon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        floor = Floor.objects.get(number=data['floor'])
        polygon = Polygon.objects.create(
            floor=floor,
            short_description=data['short_description'],
            description=data['description'],
            coordinates=json.dumps(data['coordinates'])
        )
        return JsonResponse({'status': 'success', 'id': polygon.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_polygons(request, floor_number):
    floor = Floor.objects.filter(number=floor_number).first()
    if not floor:
        return JsonResponse({'error': 'Этаж не найден'}, status=404)
    
    polygons = floor.polygons.all()
    polygon_data = [
        {
            'id': polygon.id,  # Добавляем id
            'description': polygon.description,
            'short_description': polygon.short_description,
            'coordinates': polygon.coordinates
        }
        for polygon in polygons
    ]
    return JsonResponse({'polygons': polygon_data, 'svg_path': floor.svg_path})

@csrf_exempt
def edit_polygon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            polygon = Polygon.objects.get(id=data['id'])
            polygon.short_description = data['short_description']
            polygon.description = data['description']
            polygon.save()
            return JsonResponse({'status': 'success'})
        except Polygon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Polygon not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def delete_polygon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        polygon_id = data.get('id')
        try:
            polygon = Polygon.objects.get(id=polygon_id)
            polygon.delete()
            return JsonResponse({'status': 'success', 'message': 'Полигон успешно удален'})
        except Polygon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Полигон не найден'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F

import logging

logger = logging.getLogger(__name__)

def search_polygons(request):
    query = request.GET.get('q', '')
    logger.info(f"Received search query: {query}")
    if query:
        search_query = SearchQuery(query, config='russian')
        polygons = Polygon.objects.annotate(
            rank=SearchRank(F('search_vector'), search_query)
        ).filter(search_vector=search_query).order_by('-rank')[:10]
        logger.info(f"Found {polygons.count()} polygons")
        results = [{'id': p.id, 'text': p.short_description, 'floor': p.floor.number} for p in polygons]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

# Create your views here.
