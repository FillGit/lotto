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


class FakeNumbers:
    numbers_1 = [61, 55, 7, 59, 63, 13, 49, 10, 48, 8, 22, 76, 39, 47, 75, 31, 23, 33, 87,
                 77, 20, 44, 53, 43, 6, 18, 80, 58, 28, 62, 16, 78, 84, 21, 67, 89, 90, 36,
                 79, 56, 54, 68, 46, 66, 12, 51, 72, 14, 50, 42, 17, 37, 38, 11, 64, 32, 1,
                 81, 60, 70, 41, 2, 30, 74, 52, 24, 57, 40, 15, 4, 85, 5, 34, 71, 9, 82, 35,
                 25, 86, 27, 73, 83, 3, 29, 88, 69, 65]

    numbers_2 = [60, 89, 4, 44, 36, 57, 47, 21, 62, 51, 26, 63, 29, 66, 85, 84, 17, 23, 55,
                 72, 11, 35, 67, 79, 32, 86, 5, 38, 16, 48, 33, 45, 80, 15, 88, 27, 74, 9, 49,
                 46, 40, 58, 70, 14, 37, 56, 71, 77, 83, 28, 8, 81, 34, 78, 31, 43, 68, 59,
                 87, 73, 64, 1, 42, 61, 25, 18, 39, 41, 20, 75, 54, 2, 10, 6, 50, 22, 12, 90,
                 30, 3, 53, 24, 13, 82, 69, 52, 65]

    numbers_3 = [58, 80, 72, 59, 23, 61, 70, 71, 75, 65, 82, 37, 47, 79, 2, 16, 43, 5, 60,
                 54, 19, 6, 44, 49, 78, 1, 34, 11, 14, 90, 88, 36, 27, 87, 10, 69, 73, 32,
                 17, 35, 55, 50, 20, 13, 8, 76, 25, 68, 45, 12, 64, 74, 51, 42, 26, 85, 28,
                 52, 30, 31, 41, 7, 86, 22, 46, 39, 89, 77, 84, 66, 81, 4, 29, 15, 9, 57, 18,
                 3, 21, 83, 48, 24, 53, 56, 38, 63, 33]

    numbers_4 = [84, 4, 32, 6, 14, 12, 2, 47, 29, 46, 27, 13, 44, 51, 65, 60, 8, 22, 72,
                 62, 82, 43, 37, 85, 1, 59, 3, 41, 67, 79, 89, 17, 87, 31, 73, 28, 48,
                 49, 30, 71, 20, 63, 15, 33, 52, 40, 9, 58, 77, 7, 81, 75, 50, 57, 55, 36,
                 69, 80, 83, 68, 66, 45, 10, 18, 23, 70, 16, 35, 42, 61, 34, 11, 39, 53, 88,
                 90, 26, 5, 78, 38, 19, 24, 56, 86, 74, 76, 21]

    numbers_5 = [57, 37, 76, 12, 8, 28, 77, 79, 73, 32, 86, 65, 46, 74, 1, 27, 44, 23, 56,
                 18, 38, 29, 67, 36, 69, 31, 88, 24, 49, 50, 47, 78, 6, 61, 80, 14, 87, 54,
                 83, 55, 17, 26, 21, 13, 72, 7, 70, 48, 19, 16, 42, 51, 33, 84, 52, 5, 20,
                 4, 90, 64, 75, 53, 40, 3, 62, 58, 41, 2, 25, 39, 10, 34, 63, 43, 60, 81, 35,
                 71, 66, 30, 11, 82, 68, 22, 85, 9, 45]
