from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_CHOICES = (
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
        ('admin', 'Administrador'),
    )

    rol = models.CharField(max_length=10, choices=ROL_CHOICES)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
