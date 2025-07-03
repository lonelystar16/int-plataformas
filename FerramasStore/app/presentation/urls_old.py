from django.urls import path, include
from rest_framework import routers
from FerramasStore.app.presentation import views
from app.presentation import views
from app.presentation.views import CrearPagoExternoView
from app.presentation.views import productos_externos_page
from app.presentation.views import valor_dolar_page
# Configuración del enrutador de Django REST Framework

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
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    # Rutas de la API
    path('api/', include(router.urls)),
    path('api/crear-pago-externo/', CrearPagoExternoView.as_view(), name='crear_pago_externo'),
    path('productos-externos/', productos_externos_page.as_view(), name='productos_externos'),
    path('valor-dolar/', valor_dolar_page, name='obtener_valor_dolar'),
]