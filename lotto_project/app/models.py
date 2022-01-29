from django.db import models

# Create your models here.

class Game(models.Model):
    game = models.CharField(max_length=20)
    numbers = models.CharField(max_length=200)