from django.contrib import admin
from app.domain.models import Producto, Categoria, Subscriber

# Register your models here.
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Subscriber)
