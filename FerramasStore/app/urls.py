from django.urls import path
from app.presentation import views
from app.presentation.views import crear_pago_externo_view
from app.presentation.views import productos_externos_page, valor_dolar_page, crear_pago_page, procesar_pago, voucher_view

# Configuración del namespace de la app
app_name = 'app'

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),
    
    # Rutas de productos por categoría
    path('productos/herramientas-manuales/', views.herra_manuales, name='herra_manuales'),
    path('productos/materiales-basicos/', views.materiales_basicos, name='materiales_basicos'),
    path('productos/equipos-seguridad/', views.equipos_seguridad, name='equipos_seguridad'),
    path('productos/tornillos-anclaje/', views.tornillos_anclaje, name='tornillos_anclaje'),
    path('productos/fijaciones/', views.fijaciones, name='fijaciones'),
    path('productos/equipos-medicion/', views.equipos_medicion, name='equipos_medicion'),
    
    # Rutas de autenticación
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Rutas de compra
    path('checkout/', views.checkout, name='checkout'),
    
    # Rutas de servicios externos
    path('externos/productos/', productos_externos_page, name='productos_externos_page'),
    path('externos/valor-dolar/', valor_dolar_page, name='valor_dolar_page'),
    
    # Rutas de pagos
    path('pagos/crear-pago-externo/', crear_pago_externo_view, name='crear_pago_externo'),
    path('pagos/crear/', crear_pago_page, name='crear_pago_page'),
    path('pagos/procesar/', procesar_pago, name='procesar_pago'),
    path('pagos/voucher/', voucher_view, name='voucher'),
    path('pagos/voucher/<str:token>/', voucher_view, name='voucher_token'),
]