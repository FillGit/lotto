from django.db.models import IntegerField
from django.db.models.functions import Cast

from lotto_app.app.models import Game
from lotto_app.constants import COMBINATION_OPTIONS_8_ADD


class CombinationOptions8Add():
    def __init__(self, name_game, main_game_id, how_games):
        self.name_game = name_game
        self.main_game_id = main_game_id
        self.how_games = how_games

        self.game_objs = self.get_game_objs(name_game, main_game_id, how_games)

    def get_game_objs(self, name_game, main_game_id, how_games):
        return Game.objects.filter(
            name_game=name_game,
        ).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        ).filter(
            game_id_int__lte=main_game_id,
            game_id_int__gte=main_game_id-how_games-5
        ).order_by('-game_id_int')[0:how_games]

    def _get_combination_options_8_add(self, numbers):
        combination_8_add = [1]
        numbers = list(set(numbers))
        previous_n = numbers[0]
        for n in numbers:
            if n == numbers[0]:
                pass
            elif n == previous_n + 1:
                combination_8_add[-1] += 1
                previous_n = n
            else:
                combination_8_add.append(1)
                previous_n = n
        return sorted(combination_8_add, reverse=True)

    def _get_sum_combination_options(self, combination_options):
        _sum_combination = {k: 0 for k, _ in COMBINATION_OPTIONS_8_ADD.items()}
        for name, seq in COMBINATION_OPTIONS_8_ADD.items():
            for _, combination in combination_options.items():
                if combination == seq:
                    _sum_combination[name] += 1
        return {name: seq for name, seq in _sum_combination.items() if seq != 0}

    def get_combination_options(self):
        combination_options = {game_obj.game_id: self._get_combination_options_8_add(game_obj.numbers)
                               for game_obj in self.game_objs}
        combination_options.update(self._get_sum_combination_options(combination_options))
        return combination_options
