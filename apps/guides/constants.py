from django.db import models

class ToothChoises(models.TextChoices):
    Up = 'Up', 'Верх'
    Down = 'Down', 'Низ'