from copy import deepcopy

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class Game(models.Model):
    name_game = models.CharField(max_length=25, blank=False)
    game_id = models.CharField(max_length=20, blank=False)
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name_game', 'game_id'],
                                    name='not unique name_game and game_id')
        ]

    def __str__(self):
        """
        String for representing the Model object.
        """
        return f'id: {self.id}, game_id: {self.game_id}'

    def save(self, *args, **kwargs):
        if not self.no_numbers and not self.add_numbers:
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

    @staticmethod
    def get_numbers_in_row(order_row, combination_numbers):
        _row = 1
        previous_number = list(combination_numbers)[0]
        previous_numbers = [previous_number]
        numbers_in_row = []
        for number in list(combination_numbers)[1:]:
            if number == previous_number + 1:
                _row += 1
                previous_numbers.append(number)
                if _row == order_row:
                    numbers_in_row.append(deepcopy(previous_numbers))
                elif _row > order_row:
                    numbers_in_row.pop()
                    numbers_in_row.append(deepcopy(previous_numbers))
            else:
                _row = 1
                previous_numbers = [number]
            previous_number = number
        return numbers_in_row

    @staticmethod
    def get_parts_numbers(part_consists_of, combination_numbers):
        parts = []
        i = 0
        for _ in combination_numbers:
            if (len(combination_numbers) - i - part_consists_of) < 0:
                break
            parts.append(list(combination_numbers)[i:i+part_consists_of])
            i += 1
        return parts

    def get_combination_win_ticket(self, part_consists_of, order_row):
        combination_win_ticket = set(self.get_win_list(self.last_win_number_ticket))
        return {'combination_win_ticket': combination_win_ticket,
                'parts': self.get_parts_numbers(part_consists_of, combination_win_ticket),
                'numbers_in_row': self.get_numbers_in_row(order_row, combination_win_ticket)
                }


class PurchasedTickets(models.Model):
    game_obj = models.ForeignKey(Game, on_delete=models.CASCADE)
    purchased_ticket = models.CharField(max_length=20, blank=False)
    ticket_numbers = models.CharField(max_length=20, blank=False)


class StateNumbers(models.Model):
    name_game = models.CharField(max_length=25, blank=False)
    game_id = models.CharField(max_length=20, blank=False)

    number = models.IntegerField()
    amount_used = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name_game', 'game_id', 'number'],
                                    name='not unique name_game and game_id and number')
        ]


class LottoTickets(models.Model):
    name_game = models.CharField(max_length=25, blank=False)
    game_id = models.CharField(max_length=20, blank=False)

    ticket_id = models.CharField(max_length=20)
    first_seven_numbers = ArrayField(
        models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)]),
        size=7)
    ticket_numbers = ArrayField(
        models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)]),
        size=30)
    taken_ticket = models.BooleanField(default=False)

    constraints = [
        models.UniqueConstraint(fields=['name_game', 'game_id', 'ticket_number'],
                                name='not unique name_game and game_id and ticket_number')
    ]

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
