# FerramasStore/app/security/validators.py
import re
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

def validate_chilean_phone(value):
    """
    Valida números de teléfono chilenos
    Acepta formatos: +56912345678, 56912345678, 912345678, 12345678
    """
    # Limpiar el número
    clean_number = re.sub(r'[^\d+]', '', str(value))
    
    # Patrones válidos para Chile
    patterns = [
        r'^\+569\d{8}$',  # +56912345678 (móvil)
        r'^569\d{8}$',    # 56912345678 (móvil)
        r'^9\d{8}$',      # 912345678 (móvil)
        r'^\+562\d{8}$',  # +56212345678 (fijo Santiago)
        r'^562\d{8}$',    # 5622345678 (fijo Santiago)
        r'^\d{8}$',       # 12345678 (fijo)
    ]
    
    if not any(re.match(pattern, clean_number) for pattern in patterns):
        raise ValidationError(_('Número de teléfono chileno inválido'))

def validate_chilean_rut(value):
    """
    Valida RUT chileno con dígito verificador
    """
    # Limpiar RUT
    rut = re.sub(r'[^\dKk]', '', str(value).upper())
    
    if len(rut) < 8 or len(rut) > 9:
        raise ValidationError(_('RUT debe tener entre 8 y 9 caracteres'))
    
    # Separar número y dígito verificador
    rut_number = rut[:-1]
    check_digit = rut[-1]
    
    # Calcular dígito verificador
    def calculate_check_digit(rut_num):
        multiplier = 2
        total = 0
        
        for digit in reversed(rut_num):
            total += int(digit) * multiplier
            multiplier = 3 if multiplier == 7 else multiplier + 1
        
        remainder = total % 11
        if remainder == 0:
            return '0'
        elif remainder == 1:
            return 'K'
        else:
            return str(11 - remainder)
    
    expected_digit = calculate_check_digit(rut_number)
    
    if check_digit != expected_digit:
        raise ValidationError(_('RUT inválido'))

def validate_strong_password(value):
    """
    Valida contraseñas fuertes
    """
    if len(value) < 8:
        raise ValidationError(_('La contraseña debe tener al menos 8 caracteres'))
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('La contraseña debe tener al menos una letra mayúscula'))
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('La contraseña debe tener al menos una letra minúscula'))
    
    if not re.search(r'\d', value):
        raise ValidationError(_('La contraseña debe tener al menos un número'))
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(_('La contraseña debe tener al menos un carácter especial'))

def validate_no_sql_injection(value):
    """
    Valida que no haya intentos de inyección SQL
    """
    sql_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
        r'(\bunion\b.*\bselect\b)',
        r'(\bor\b\s*\d+\s*=\s*\d+)',
        r'(\band\b\s*\d+\s*=\s*\d+)',
        r'(\'\s*or\s*\'\d+\'\s*=\s*\'\d+)',
        r'(;|\-\-|\/\*|\*\/)',
        r'(\bxp_\w+)',
        r'(\bsp_\w+)',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, str(value), re.IGNORECASE):
            raise ValidationError(_('Entrada no válida detectada'))

def sanitize_html_input(value):
    """
    Sanitiza entrada HTML para prevenir XSS
    """
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    allowed_attributes = {}
    
    return bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def validate_email_domain(value):
    """
    Valida email y dominio
    """
    validate_email(value)
    
    # Lista de dominios bloqueados (ejemplo)
    blocked_domains = [
        '10minutemail.com',
        'guerrillamail.com',
        'mailinator.com',
        'tempmail.org'
    ]
    
    domain = value.split('@')[1].lower()
    if domain in blocked_domains:
        raise ValidationError(_('Dominio de email no permitido'))

def validate_safe_filename(value):
    """
    Valida nombres de archivos seguros
    """
    if not value:
        raise ValidationError(_('Nombre de archivo requerido'))
    
    # Caracteres no permitidos
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(_('Nombre de archivo contiene caracteres no permitidos'))
    
    # Extensiones peligrosas
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.jar', '.php', '.asp', '.jsp']
    
    for ext in dangerous_extensions:
        if value.lower().endswith(ext):
            raise ValidationError(_('Tipo de archivo no permitido'))

def validate_price_range(value):
    """
    Valida rangos de precios razonables
    """
    if value < 0:
        raise ValidationError(_('El precio no puede ser negativo'))
    
    if value > 10000000:  # 10 millones CLP
        raise ValidationError(_('Precio excede el límite máximo'))

def validate_quantity(value):
    """
    Valida cantidades de productos
    """
    if value < 0:
        raise ValidationError(_('La cantidad no puede ser negativa'))
    
    if value > 10000:
        raise ValidationError(_('Cantidad excede el límite máximo'))

def validate_address(value):
    """
    Valida direcciones
    """
    if len(value.strip()) < 5:
        raise ValidationError(_('La dirección debe tener al menos 5 caracteres'))
    
    # Sanitizar para XSS
    sanitized = sanitize_html_input(value)
    if sanitized != value:
        raise ValidationError(_('La dirección contiene caracteres no permitidos'))

class SecureFormMixin:
    """
    Mixin para formularios con validaciones de seguridad automáticas
    """
    def clean(self):
        cleaned_data = super().clean()
        
        # Aplicar sanitización a todos los campos de texto
        for field_name, value in cleaned_data.items():
            if isinstance(value, str):
                # Validar contra inyección SQL
                try:
                    validate_no_sql_injection(value)
                except ValidationError:
                    self.add_error(field_name, 'Entrada no válida detectada')
                
                # Sanitizar HTML
                cleaned_data[field_name] = sanitize_html_input(value)
        
        return cleaned_data
