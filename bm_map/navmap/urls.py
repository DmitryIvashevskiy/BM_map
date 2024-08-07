from django.urls import path
from . import views

urlpatterns = [
    path('', views.map, name='index'),
    path('admin_map/', views.admin_map, name='admin_map'),
    path('get_polygons/<int:floor_number>/', views.get_polygons, name='get_polygons'),
    path('add_polygon/', views.add_polygon, name='add_polygon'),
    path('edit_polygon/', views.edit_polygon, name='edit_polygon'),
    path('delete_polygon/', views.delete_polygon, name='delete_polygon'),
    path('search_polygons/', views.search_polygons, name='search_polygons'),
]
