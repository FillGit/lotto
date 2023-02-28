from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.


class Game(models.Model):
    game = models.CharField(max_length=20, blank=False, unique=True)
    numbers = models.CharField(max_length=2000)
    last_win_number_card = models.PositiveIntegerField(blank=True, null=True,
                                                       validators=[MinValueValidator(1)])
    last_win_number_ticket = models.PositiveIntegerField(blank=True, null=True,
                                                         validators=[MinValueValidator(1)])
    no_numbers = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return f'id: {self.id}, game: {self.game}'

    def save(self, *args, **kwargs):
        if not self.no_numbers:
            self.no_numbers = self.get_no_numbers()
        super().save(*args, **kwargs)

    def get_no_numbers(self):
        list_numbers = [int(num) for num in self.numbers.split(' ')]
        no_numbers = [str(num) for num in
                      sorted([num for num in range(1, 91) if num not in list_numbers])]
        if no_numbers:
            return ' '.join(no_numbers)
        return None


class PurchasedTickets(models.Model):
    game_obj = models.ForeignKey(Game, on_delete=models.CASCADE)
    purchased_ticket = models.CharField(max_length=20, blank=False)
    ticket_numbers = models.CharField(max_length=20, blank=False)


class StateNumbers(models.Model):
    game_obj = models.ForeignKey(Game, on_delete=models.CASCADE)

    number = models.IntegerField()
    state = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game_obj', 'number'], name='not unique game and number')
        ]


class LottoTickets(models.Model):
    game_obj = models.ForeignKey(Game, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=20)
    first_seven_numbers = models.CharField(max_length=20)
    ticket_all_numbers = models.CharField(max_length=500)
    taken_ticket = models.BooleanField(default=False)

    constraints = [
        models.UniqueConstraint(fields=['game_obj', 'ticket_number'],
                                name='not unique game and ticket_number')
    ]
