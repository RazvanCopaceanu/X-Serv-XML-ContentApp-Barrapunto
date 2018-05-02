from django.db import models

# Create your models here.

class Persona(models.Model):
    nombre = models.CharField(max_length=32)
    descripcion = models.TextField()
    def __str__(self):
        return self.nombre
