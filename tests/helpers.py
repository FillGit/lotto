from random import shuffle

from lotto_app.app.models import Game

"""
Default win_card and win_ticket of the GameFactory class:

    default
        "win_card": {"by_account": 35, "last_win_number_ticket": xxx}
        "win_ticket": {"by_account": 60, "last_win_number_ticket": xxx}

    default in_order_numbers = True
        "win_card": {"by_account": 35, "last_win_number_ticket": 35}
        "win_ticket": {"by_account": 60, "last_win_number_ticket": 60}

    default get_game_auto_win_json()
        "win_card": {"by_account": 37, "last_win_number_ticket": xxx}
        "win_ticket": {"by_account": 62, "last_win_number_ticket": xxx}
"""


class GameFactory():

    def __init__(self, name_game='test_lotto1', amount_games=3, game_ids=[], numbers_in_lotto=90,
                 no_numbers_in_lotto=3, fields_games=None, in_order_numbers=False, only_games_json=False):

        self.name_game = name_game
        self.amount_games = amount_games
        self.game_ids = game_ids
        self.numbers_in_lotto = numbers_in_lotto
        self.no_numbers_in_lotto = no_numbers_in_lotto
        self.fields_games = fields_games
        self.in_order_numbers = in_order_numbers
        self.only_games_json = only_games_json

        if fields_games:
            self.set_games_db()
        elif only_games_json is False:
            self.fields_games = self.get_fields_games()
            self.set_games_db()
        elif only_games_json:
            self.fields_games = self.get_fields_games()

    def get_no_numbers(self, numbers, numbers_in_lotto):
        no_numbers = [num for num in
                      sorted([num for num in range(1, numbers_in_lotto+1) if num not in numbers])]
        if no_numbers:
            return no_numbers
        return None

    def get_fields(self, game_id):
        if self.in_order_numbers:
            numbers = [n for n in range(1, self.numbers_in_lotto-self.no_numbers_in_lotto+1)]
            last_win_number_card = 35
            last_win_number_ticket = 60
        else:
            list_numbers = list(range(1, self.numbers_in_lotto+1))
            shuffle(list_numbers)
            numbers = [n for n in list_numbers[0:self.numbers_in_lotto-self.no_numbers_in_lotto]]
            last_win_number_card = list_numbers[35]
            last_win_number_ticket = list_numbers[60]
        return {
            'name_game': self.name_game,
            'game_id': game_id,
            'numbers': numbers,
            'last_win_number_card': last_win_number_card,
            'last_win_number_ticket': last_win_number_ticket,
            'no_numbers': self.get_no_numbers(numbers, self.numbers_in_lotto)
        }

    def get_fields_games(self):
        if not self.game_ids:
            game_objs = Game.objects.filter(name_game=self.name_game).all()
            start = 1 if not game_objs else int(game_objs.last().game_id)+1
            _game_ids = [_id for _id in range(start, start+self.amount_games)]
            return [self.get_fields(_id) for _id in _game_ids]

        return [self.get_fields(_id) for _id in self.game_ids]

    def set_games_db(self):
        return Game.objects.bulk_create([Game(**fields) for fields in self.fields_games])

    def _add_zero(self, number=None):
        str_number = str(number)
        if len(str_number) > 1:
            return str_number
        return f'0{str_number}'

    def get_game_json(self, index=0):
        return self.fields_games[index]

    def get_game_str_numbers_json(self, index=0):
        _fields_game = self.fields_games[index]
        return {
            'name_game': _fields_game['name_game'],
            'game_id': _fields_game['game_id'],
            'str_numbers': ' '.join([self._add_zero(num) for num in _fields_game['numbers']]),
            'last_win_number_card': _fields_game['last_win_number_card'],
            'last_win_number_ticket': _fields_game['last_win_number_ticket'],
            'str_no_numbers': ' '.join([self._add_zero(num) for num in _fields_game['no_numbers']])
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
        _fields_game = self.get_game_str_numbers_json()
        auto_win_numbers = self._get_auto_win_numbers(_fields_game['str_numbers'],
                                                      line, win_card_by_account, win_ticket_by_account)
        return {
            'name_game': _fields_game['name_game'],
            'game_id': _fields_game['game_id'],
            'str_numbers': auto_win_numbers,
            'auto_win': True,
        }
