from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class Game(models.Model):
    name_game = models.CharField(max_length=25, blank=False)
    game_id = models.CharField(max_length=20, blank=False, unique=True)
    numbers = ArrayField(
        models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)]),
        size=90)

    last_win_number_card = models.PositiveIntegerField(blank=True, null=True,
                                                       validators=[MinValueValidator(1)])
    last_win_number_ticket = models.PositiveIntegerField(blank=True, null=True,
                                                         validators=[MinValueValidator(1)])

    no_numbers = ArrayField(
        models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(89)]),
        size=89, blank=True, null=True)

    add_numbers = ArrayField(
        models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(89)]),
        size=89, blank=True, null=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return f'id: {self.id}, game: {self.game_id}'

    def save(self, *args, **kwargs):
        if not self.no_numbers:
            self.no_numbers = self.get_no_numbers()
        super().save(*args, **kwargs)

    def get_no_numbers(self):
        no_numbers = [num for num in sorted([num for num in range(1, 91) if num not in self.numbers])]
        if no_numbers:
            return no_numbers
        return None

    def get_win_list(self, last_win_number=None):
        if not last_win_number:
            last_win_number = self.last_win_number_ticket

        win_list = []
        for num in self.numbers:
            win_list.append(num)
            if last_win_number == num:
                break
        return win_list

    def _get_win(self, name_last_win_number, last_win_number):
        if not last_win_number:
            return {name_last_win_number: None,
                    'by_account': None
                    }
        win_list = self.get_win_list(last_win_number)
        return {'by_account': len(win_list),
                name_last_win_number: last_win_number}

    def get_win_card(self):
        return self._get_win('last_win_number_card', self.last_win_number_card)

    def get_win_ticket(self):
        return self._get_win('last_win_number_ticket', self.last_win_number_ticket)

    @staticmethod
    def record_correction_numbers(str_numbers: str, cut_first_zero=False) -> list[str]:
        game_numbers = []
        for str_num in [num for num in str_numbers.replace(' ', ',').split(',') if num]:
            if str_num[0] == '0' and cut_first_zero:
                game_numbers.append(str_num[1])
            else:
                game_numbers.append(str_num)
        return game_numbers

    @staticmethod
    def get_list_str_numbers(str_numbers, cut_first_zero=False):
        _val = str_numbers.replace(' ', '')
        return Game.record_correction_numbers(
            " ".join([_val[i:i+2] for i in range(0, len(_val), 2)]), cut_first_zero
        )

    def get_game_numbers(self):
        return list(map(int, self.record_correction_numbers(self.numbers)))


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
        return [int(num) for num in self.ticket_numbers.split(' ') if num]

    def get_first_seven_numbers(self) -> list:
        return [int(num) for num in self.first_seven_numbers.split(' ') if num]

    @staticmethod
    def get_tickets_plus(dict_tickets):
        dict_tickets_plus = {}
        for key, value in dict_tickets.items():
            dict_tickets_plus[key] = {'numbers': value['numbers'],
                                      'line_1_1': value['numbers'][0:5],
                                      'line_1_2': value['numbers'][5:10],
                                      'line_1_3': value['numbers'][10:15],
                                      'line_2_1': value['numbers'][15:20],
                                      'line_2_2': value['numbers'][20:25],
                                      'line_2_3': value['numbers'][25:30],
                                      'card_1': value['numbers'][0:15],
                                      'card_2': value['numbers'][15:30]
                                      }
        return dict_tickets_plus
