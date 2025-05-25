from django.db import models
from app.domain.models import *

# Create your models here.

# Nuevo modelo para suscriptores
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email 