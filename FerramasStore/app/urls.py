from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('herra-manuales/', views.herra_manuales, name='herra_manuales'),
    path('materiales-basicos/', views.materiales_basicos, name='materiales_basicos'),
    path('equipos-seguridad/', views.equipos_seguridad, name='equipos_seguridad'),
    path('tornillos-anclaje/', views.tornillos_anclaje, name='tornillos_anclaje'),
    path('fijaciones/', views.fijaciones, name='fijaciones'),
    path('equipos-medicion/', views.equipos_medicion, name='equipos_medicion'),
]