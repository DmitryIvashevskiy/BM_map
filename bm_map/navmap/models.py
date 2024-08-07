from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Floor(MPTTModel):
    number = models.IntegerField(unique=True)
    svg_path = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['number']

    def __str__(self):
        return f'Этаж {self.number}'

class Polygon(MPTTModel):
    floor = TreeForeignKey(Floor, on_delete=models.CASCADE, related_name='polygons')
    description = models.TextField(max_length=500)
    short_description = models.CharField(max_length=255)
    coordinates = models.TextField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    search_vector = SearchVectorField(null=True)

    class MPTTMeta:
        order_insertion_by = ['short_description']

    class Meta:
        indexes = [GinIndex(fields=['search_vector'])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем поле search_vector
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE navmap_polygon SET search_vector = to_tsvector('russian', coalesce(short_description, '') || ' ' || coalesce(description, '')) WHERE id = %s",
                [self.id]
            )

    def __str__(self):
        return self.short_description
# Create your models here.
