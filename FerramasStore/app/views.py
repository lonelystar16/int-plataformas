from django.shortcuts import render

def index(request):
    return render(request, 'pages/index.html')

def herra_manuales(request):
    return render(request, 'pages/herra-manuales.html')

def materiales_basicos(request):
    return render(request, 'pages/materiales-basicos.html')

def equipos_seguridad(request):
    return render(request, 'pages/equipos-seguridad.html')

def tornillos_anclaje(request):
    return render(request, 'pages/tornillos-anclaje.html')

def fijaciones(request):
    return render(request, 'pages/fijaciones.html')

def equipos_medicion(request):
    return render(request, 'pages/equipos-medicion.html')

