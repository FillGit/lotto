from copy import deepcopy
from random import shuffle

from lotto_app.app.models import Game


class GameFactory():

    def __init__(self, amount_games=3, game_ids=[], numbers_in_lotto=90, no_numbers_in_lotto=3,
                 fields_games=None, only_games_json=False):

        self.amount_games = amount_games
        self.game_ids = game_ids
        self.numbers_in_lotto = numbers_in_lotto
        self.no_numbers_in_lotto = no_numbers_in_lotto
        self.fields_games = fields_games
        self.only_games_json = only_games_json

        if fields_games:
            self.set_games_db()
        elif only_games_json is False:
            self.fields_games = self.get_fields_games()
            self.set_games_db()
        elif only_games_json:
            self.fields_games = self.get_fields_games()

    def get_no_numbers(self, numbers, numbers_in_lotto):
        list_numbers = [int(num) for num in numbers.split(' ')]
        no_numbers = [str(num) for num in
                      sorted([num for num in range(1, numbers_in_lotto+1) if num not in list_numbers])]
        if no_numbers:
            return ' '.join(no_numbers)
        return None

    def get_fields(self, game_id, numbers_in_lotto, no_numbers_in_lotto):
        list_numbers = list(range(1, numbers_in_lotto+1))
        shuffle(list_numbers)
        numbers = ' '.join([str(n) for n in list_numbers[0:numbers_in_lotto-no_numbers_in_lotto]])
        return {
            'game': game_id,
            'numbers': numbers,
            'last_win_number_card': list_numbers[35],
            'last_win_number_ticket': list_numbers[60],
            'no_numbers': self.get_no_numbers(numbers, numbers_in_lotto)
        }

    def get_fields_games(self):
        if not self.game_ids:
            game_objs = Game.objects.all()
            start = 1 if not game_objs else int(game_objs.last().game)+1
            game_ids = [_id for _id in range(start, start+self.amount_games)]

        return [self.get_fields(_id, self.numbers_in_lotto, self.no_numbers_in_lotto) for _id in game_ids]

    def set_games_db(self):
        return Game.objects.bulk_create([Game(**fields) for fields in self.fields_games])

    def _add_zero(self, str_number=None):
        if len(str_number) > 1:
            return str_number
        return f'0{str_number}'

    def get_game_json(self, index=0):
        _fields_game = deepcopy(self.fields_games[index])
        return {
            'game': _fields_game['game'],
            'numbers': ' '.join([self._add_zero(num) for num in _fields_game['numbers'].split(' ')]),
            'last_win_number_card': _fields_game['last_win_number_card'],
            'last_win_number_ticket': _fields_game['last_win_number_ticket'],
            'no_numbers': ' '.join([self._add_zero(num) for num in _fields_game['no_numbers'].split(' ')])
        }

    def _get_auto_win_numbers(self, numbers, line, win_card_by_account, win_ticket_by_account):
        list_str_numbers = numbers.split(' ')
        list_auto_win_numbers = []
        list_auto_win_numbers.append(''.join(list_str_numbers[0:line]))
        list_auto_win_numbers.append(''.join(list_str_numbers[line:win_card_by_account]))
        list_auto_win_numbers.append(''.join(list_str_numbers[win_card_by_account:win_ticket_by_account]))
        list_auto_win_numbers.extend(list_str_numbers[win_ticket_by_account:])
        return ' '.join(list_auto_win_numbers)

    def get_game_auto_win_json(self, line=7, win_card_by_account=37, win_ticket_by_account=62):
        _fields_game = self.get_game_json()
        auto_win_numbers = self._get_auto_win_numbers(_fields_game['numbers'],
                                                      line, win_card_by_account, win_ticket_by_account)
        return {
            'game': _fields_game['game'],
            'numbers': auto_win_numbers,
            'auto_win': True,
        }
