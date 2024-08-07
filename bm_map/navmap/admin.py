from django.contrib import admin
from .models import Floor, Polygon

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('number', 'svg_path')
    search_fields = ('number',)

@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'floor', 'description')
    search_fields = ('short_description', 'floor__number')
    fields = ('floor', 'short_description', 'description', 'coordinates')




# Register your models here.
