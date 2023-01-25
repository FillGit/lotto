from django.db import models

# Create your models here.

class Game(models.Model):
    game = models.CharField(max_length=20, blank=False, unique=True)
    numbers = models.CharField(max_length=2000)


class PurchasedTickets(models.Model):
    game_obj = models.ForeignKey(Game, on_delete = models.CASCADE)
    purchased_ticket = models.CharField(max_length=20, blank=False)
    ticket_numbers = models.CharField(max_length=20, blank=False)


class StateNumbers(models.Model):
    game_obj = models.ForeignKey(Game, on_delete = models.CASCADE)

    number = models.IntegerField()
    state = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game_obj', 'number'], name='not unique game and number')
        ]