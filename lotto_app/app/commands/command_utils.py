from statistics import mean, median

from django.db.models import IntegerField
from django.db.models.functions import Cast

from lotto_app.app.models import Game
from lotto_app.config import get_from_config
from lotto_app.constants import COMBINATION_OPTIONS_8_ADD


class Utils8Add():
    def __init__(self, name_game, main_game_id, how_games, game_objs=None):
        self.name_game = name_game
        self.main_game_id = main_game_id
        self.how_games = how_games
        self.numbers_in_lotto = int(get_from_config('lotto_8_add',
                                                    f'numbers_in_lotto_{name_game}'))
        if not game_objs:
            self.game_objs = self._get_game_objs(name_game, main_game_id, how_games)
        else:
            self.game_objs = game_objs

    def _get_game_objs(self, name_game, main_game_id, how_games):
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

    def get_game_combinations(self, how_info_games=None):
        if not how_info_games:
            return {game_obj.game_id: self._get_combination_options_8_add(game_obj.numbers)
                    for game_obj in self.game_objs}
        return {game_obj.game_id: self._get_combination_options_8_add(game_obj.numbers)
                for game_obj in self.game_objs[0:how_info_games]}


class CombinationOptions8Add(Utils8Add):
    def get_sum_combination_options(self, game_combinations=None):
        if not game_combinations:
            game_combinations = self.get_game_combinations()

        _sum_combination = {k: 0 for k, _ in COMBINATION_OPTIONS_8_ADD.items()}
        for name, seq in COMBINATION_OPTIONS_8_ADD.items():
            for _, combination in game_combinations.items():
                if combination == seq:
                    _sum_combination[name] += 1
        return {name: seq for name, seq in _sum_combination.items() if seq != 0}


class InfoSequence8Add(Utils8Add):
    def get_info_sequence(self, sequence, game_obj, previous_game_id=None):
        info = {}
        if not previous_game_id:
            previous_game_id = self.game_objs[0].game_id

        if set(sequence).issubset(set(game_obj.numbers)):
            info[game_obj.game_id] = game_obj.game_id
            info['previous game_id'] = previous_game_id
            info['difference'] = int(previous_game_id) - int(game_obj.game_id)
        return info

    def get_all_info_sequence(self, sequence, only_len_sequence=False, how_info_games=None):
        info = []
        len_sequence = len(sequence)
        if not how_info_games:
            game_combinations = self.get_game_combinations()
            game_objs_by_game_id = {_obj.game_id: _obj for _obj in self.game_objs}
        else:
            game_combinations = self.get_game_combinations(how_info_games)
            game_objs_by_game_id = {_obj.game_id: _obj for _obj in self.game_objs[0:how_info_games]}
        previous_game_id = self.game_objs[0].game_id
        for game_id, combination in game_combinations.items():
            _inf = self.get_info_sequence(sequence,
                                          game_objs_by_game_id[game_id],
                                          previous_game_id)
            if _inf and not only_len_sequence and len_sequence <= max(combination):
                info.append(_inf)
                previous_game_id = game_id
            if _inf and only_len_sequence and len_sequence in combination:
                info.append(_inf)
                previous_game_id = game_id
        return info

    def get_info_difference(self, all_info_sequence):
        differences = [_info['difference'] for _info in all_info_sequence]
        if not differences:
            return {'amount_sequence': 0}
        return {'min_difference': min(differences),
                'middle_difference': mean(differences),
                'max_difference': max(differences),
                'median': median(differences),
                'amount_sequence': len(all_info_sequence)}

    def validate_sequence(self, sequence):
        if len({isinstance(_i, int) for _i in sequence}) != 1:
            return False
        if not set(sequence).issubset(set([_i for _i in range(1, self.numbers_in_lotto+1)])):
            return False
        len_sequence = len(sequence)
        first_number = sequence[0]
        expect_sequence = [_n + first_number for _n in range(0, len_sequence)]
        if sequence != expect_sequence:
            return False
        return True

    def get_all_sequences_in_games(self, part_consists_of, how_info_games):
        all_sequences = Game.get_parts_numbers(part_consists_of,
                                               [_i for _i in range(1, self.numbers_in_lotto+1)])
        all_sequences_in_games = {}
        for sequence in all_sequences:
            all_info_sequence = self.get_all_info_sequence(sequence, False, how_info_games)
            all_sequences_in_games[str(sequence)] = self.get_info_difference(all_info_sequence)['amount_sequence']
        return all_sequences_in_games


class Probabilities8Add(InfoSequence8Add):
    def get_count_sequences(self, part_consists_of, steps_back_games, limit):
        return {name_seq: sum
                for name_seq, sum in self.get_all_sequences_in_games(part_consists_of,
                                                                     steps_back_games).items()
                if sum >= limit
                }
