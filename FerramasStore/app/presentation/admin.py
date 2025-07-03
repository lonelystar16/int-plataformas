from django.contrib import admin
from app.domain.models import Producto, Categoria, Subscriber, Pago

# Register your models here.
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Subscriber)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['numero_voucher', 'get_comprador_display', 'metodo_pago', 'total', 'fecha']
    list_filter = ['metodo_pago', 'fecha']
    search_fields = ['numero_voucher', 'comprador__username', 'comprador__first_name']
    readonly_fields = ['id', 'fecha', 'numero_voucher']
    
    def get_comprador_display(self, obj):
        if obj.comprador:
            return f"{obj.comprador.username} (Registrado)"
        else:
            return "Cliente invitado"
    get_comprador_display.short_description = 'Comprador'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['comprador', 'productos_json']
        return self.readonly_fields
