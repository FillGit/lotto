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

    def get_win_list(self, last_win_number=None):
        if not last_win_number:
            last_win_number = self.last_win_number_ticket

        win_list = []
        for num in self.get_game_numbers():
            if int(num) == last_win_number:
                win_list.append(num)
                break
            win_list.append(num)
        return win_list

    def _get_win(self, str_last_win_number, last_win_number):
        if not last_win_number:
            return {str_last_win_number: None,
                    'amount_of_numbers': None
                    }
        win_list = self.get_win_list(last_win_number)
        return {'amount_of_numbers': len(win_list),
                str_last_win_number: last_win_number}

    def get_win_card(self):
        return self._get_win('last_win_number_card', self.last_win_number_card)

    def get_win_ticket(self):
        return self._get_win('last_win_number_ticket', self.last_win_number_ticket)

    @staticmethod
    def record_correction_numbers(str_game_numbers: list) -> list:
        game_numbers = []
        for str_num in [num for num in str_game_numbers.replace(' ', ',').split(',') if num]:
            if str_num[0] == '0':
                game_numbers.append(str_num[1])
            else:
                game_numbers.append(str_num)
        return game_numbers

    def get_game_numbers(self):
        return self.record_correction_numbers(self.numbers)


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
    ticket_id = models.CharField(max_length=20)
    first_seven_numbers = models.CharField(max_length=20)
    ticket_numbers = models.CharField(max_length=500)
    taken_ticket = models.BooleanField(default=False)

    constraints = [
        models.UniqueConstraint(fields=['game_obj', 'ticket_number'],
                                name='not unique game and ticket_number')
    ]

    def get_ticket_numbers(self) -> list:
        return [num for num in self.ticket_numbers.split(' ') if num]

    def get_first_seven_numbers(self) -> list:
        return [num for num in self.first_seven_numbers.split(' ') if num]
