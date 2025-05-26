from django.urls import path, include
from rest_framework import routers
from FerramasStore.app.presentation import views

router = routers.DefaultRouter()
router.register(r'productos', views.ProductoViewSet)
router.register(r'categorias', views.CategoriaViewSet)

urlpatterns = [
    # Rutas para las páginas del sitio web
    path('', views.index, name='index'),
    path('herra-manuales/', views.herra_manuales, name='herra_manuales'),
    path('materiales-basicos/', views.materiales_basicos, name='materiales_basicos'),
    path('equipos-seguridad/', views.equipos_seguridad, name='equipos_seguridad'),
    path('tornillos-anclaje/', views.tornillos_anclaje, name='tornillos_anclaje'),
    path('fijaciones/', views.fijaciones, name='fijaciones'),
    path('equipos-medicion/', views.equipos_medicion, name='equipos_medicion'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    # Rutas de la API
    path('api/', include(router.urls)),
]