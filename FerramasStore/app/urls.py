from django.urls import path, include
from rest_framework import routers
from app.presentation import views
from app.presentation.views import CrearPagoExternoView
from app.presentation.views import productos_externos_page, valor_dolar_page, crear_pago_page

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
    path('checkout/', views.checkout, name='checkout'),
    path('logout/', views.logout_view, name='logout'),
    # Rutas de la API
    path('api/', include(router.urls)),
    path('crear-pago-externo/', CrearPagoExternoView.as_view(), name='crear_pago_externo'),
    # Rutas para las páginas de productos externos y valor del dólar
    path('productos-externos/', productos_externos_page, name='productos_externos_page'),
    path('valor-dolar/', valor_dolar_page, name='valor_dolar_page'),
    path('crear-pago/', crear_pago_page, name='crear_pago_page'),
]