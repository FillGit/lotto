from random import shuffle
from statistics import mean, median

from django.db.models import IntegerField
from django.db.models.functions import Cast
from webtest.app import AppError

from lotto_app.app.models import Game
from lotto_app.app.utils import str_to_list_of_int
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
    def _get_probability_objs(self, game_id, steps_back_games, gen_objs):
        ids = [str(_id) for _id in range(int(game_id), int(game_id) - steps_back_games, -1)]
        return [obj for obj in gen_objs if obj.game_id in ids]

    def get_count_sequences(self, part_consists_of, steps_back_games, limit):
        return {name_seq: sum
                for name_seq, sum in self.get_all_sequences_in_games(part_consists_of,
                                                                     steps_back_games).items()
                if sum >= limit
                }

    def get_exceeding_limit_overlap(self, ng, _id,
                                    part_consists_of, steps_back_games,
                                    limit_overlap, gen_probability):
        _p8add = Probabilities8Add(
            ng, _id, steps_back_games,
            game_objs=gen_probability._get_probability_objs(_id, steps_back_games,
                                                            gen_probability.game_objs)
        )
        return _p8add.get_count_sequences(
            part_consists_of,
            steps_back_games,
            limit_overlap), _p8add.game_objs

    def get_comparison_last_game(self, gen_probability):
        comparison_last_game = {}
        game_objs = [obj for obj in gen_probability.game_objs]
        i = 1
        for _obj in game_objs[:-1]:
            set_common_numbers = set(_obj.numbers) & set(gen_probability.game_objs[i].numbers)
            comparison_last_game[_obj.game_id] = len(set_common_numbers)
            i += 1
        return comparison_last_game

    def get_shuffle_numbers(self, numbers, max_numbers=[]):
        shuffle(numbers)
        _n = []
        _n.extend(max_numbers)
        for n in numbers[0:8]:
            if len(_n) == 8:
                break
            if n not in _n:
                _n.append(n)
        return _n

    def get_favorite_option(self, favorite_option, _numbers=None, max_numbers=[]):
        if not _numbers:
            _numbers = [n for n in range(1, self.numbers_in_lotto + 1)]
        for i in range(300):
            random_numbers = self.get_shuffle_numbers(_numbers, max_numbers)
            sort_numbers = self._get_combination_options_8_add(random_numbers)
            if sort_numbers == COMBINATION_OPTIONS_8_ADD[favorite_option]:
                break
        return random_numbers

    def get_max_numbers_in_games(self, ng, _id, steps_back_games, gen_probability):
        _p8add = Probabilities8Add(
            ng, _id, steps_back_games,
            game_objs=gen_probability._get_probability_objs(_id, steps_back_games,
                                                            gen_probability.game_objs)
        )
        _all_numbers = []
        for _obj in _p8add.game_objs:
            _all_numbers.extend(_obj.numbers)
        _count_numbers = {i: 0 for i in range(1, gen_probability.numbers_in_lotto + 1)}
        for num in _all_numbers:
            _count_numbers[num] += 1
        return [i for i in dict((x, y) for x, y in sorted(_count_numbers.items(),
                                                          key=lambda x: x[1],
                                                          reverse=True))]

    def get_search_needed_combinations(self, name_combination, steps_back_more_2, steps_back_co):
        game_combinations = self.get_game_combinations()
        needed_sequences = []
        for game_id, combinations in game_combinations.items():
            if self.will_be_possible_sequence(game_combinations,
                                              steps_back_more_2, name_combination, steps_back_co,
                                              int(game_id)-1):
                needed_sequences.append({game_id: combinations})

        return needed_sequences

    def _checking_combination_options_8_add(self, name_combination, first_id, steps_back_co, game_combinations):
        for _id in range(int(first_id), int(first_id)-steps_back_co, -1):
            if str(_id) not in game_combinations:
                return True
            if game_combinations[str(_id)] == COMBINATION_OPTIONS_8_ADD[name_combination]:
                return True
        return False

    def will_be_possible_sequence(self, game_combinations,
                                  steps_back_more_2, name_combination, steps_back_co, first_id=None):
        if not first_id:
            for k, _ in game_combinations:
                if first_id:
                    break
                else:
                    first_id = k

        a_steps_back_ids = [str(_id) for _id in range(int(first_id), int(first_id)-steps_back_more_2, -1)]
        _last_id = str(a_steps_back_ids[-1])
        if _last_id not in game_combinations:
            return True

        b_steps_back_ids = [str(_id) for _id in range(int(first_id), int(first_id)-steps_back_more_2, -1)
                            if game_combinations[str(_id)][0] >= 3]
        if a_steps_back_ids != b_steps_back_ids:
            return False

        if not steps_back_co:
            steps_back_co = steps_back_more_2

        if self._checking_combination_options_8_add(name_combination, first_id, steps_back_co,
                                                    game_combinations):
            return False
        return True


class Probabilities8AddOneNumber():

    def _part_previous(self, ng, previous_id, steps_back_games_previous, gen_probability):
        return InfoSequence8Add(
            ng, previous_id, steps_back_games_previous,
            game_objs=gen_probability._get_probability_objs(previous_id, steps_back_games_previous,
                                                            gen_probability.game_objs))

    def part_big(self, ng, big_id, steps_back_games_big, gen_probability):
        return InfoSequence8Add(
            ng, big_id, steps_back_games_big,
            game_objs=gen_probability._get_probability_objs(big_id, steps_back_games_big,
                                                            gen_probability.game_objs))

    def _list_repeat(self, i_s, steps_back_games):
        list_repeat = []
        for str_number, sum in i_s.get_all_sequences_in_games(1, steps_back_games).items():
            if sum == steps_back_games:
                list_repeat.extend(str_to_list_of_int(str_number))
        return list_repeat

    def get_set_one_numbers_by_previous(self, ng, previous_id,
                                        steps_back_games_previous,
                                        gen_probability):
        part_previous = self._part_previous(ng, previous_id, steps_back_games_previous, gen_probability)
        return set(
            self._list_repeat(part_previous,
                              len([pp for pp in part_previous.game_objs]))
        )

    def get_set_one_numbers_by_big(self, ng, part_big,
                                   steps_back_games_small, gen_probability):
        list_one_numbers = []
        for obj in part_big.game_objs:
            i_s = InfoSequence8Add(ng, obj.game_id, steps_back_games_small,
                                   game_objs=gen_probability._get_probability_objs(obj.game_id,
                                                                                   steps_back_games_small,
                                                                                   gen_probability.game_objs))
            list_one_numbers.extend(self._list_repeat(i_s, steps_back_games_small))
        return set(list_one_numbers)

    def get_probability_one_number(self, ng, previous_id,
                                   steps_back_games_previous,
                                   steps_back_games_small,
                                   steps_back_games_big,
                                   gen_probability):
        big_id = previous_id - steps_back_games_previous
        part_big = self.part_big(ng, big_id, steps_back_games_big, gen_probability)
        set_one_numbers_by_big = self.get_set_one_numbers_by_big(
            ng, part_big,
            steps_back_games_small,
            gen_probability
        )
        set_one_numbers_by_previous = self.get_set_one_numbers_by_previous(
            ng, previous_id,
            steps_back_games_previous,
            gen_probability
        )

        _set_one_numbers = set_one_numbers_by_big & set_one_numbers_by_previous
        set_one_numbers = _set_one_numbers if (
            set_one_numbers_by_big and set_one_numbers_by_previous and _set_one_numbers and not (
                _set_one_numbers & set(part_big.game_objs[0].numbers))) else set()

        return set_one_numbers_by_previous, set_one_numbers

    def probability_one_number(self, ng, game_start, how_games,
                               steps_back_games_previous,
                               steps_back_games_small,
                               steps_back_games_big):
        game_end = game_start - how_games
        probability_one_number = {}
        gen_probability = Probabilities8Add(
            ng, game_start,
            how_games + steps_back_games_previous + steps_back_games_big
        )
        gen_obj_end = [_obj for _obj in gen_probability.game_objs][-1]
        if int(gen_obj_end.game_id) != game_end - steps_back_games_previous - steps_back_games_big + 1:
            raise AppError("There are not enough objects!")

        for obj in gen_probability.game_objs:
            if game_end and int(obj.game_id) > game_end:
                previous_id = int(obj.game_id)-1

                set_one_numbers_by_previous, set_one_numbers = self.get_probability_one_number(
                    ng, previous_id,
                    steps_back_games_previous,
                    steps_back_games_small,
                    steps_back_games_big,
                    gen_probability
                )

                if set_one_numbers:
                    probability_one_number[obj.game_id] = {
                        'obj.numbers': obj.numbers,
                        'set_one_numbers': set_one_numbers,
                        'set_one_numbers_by_previous': set_one_numbers_by_previous,
                        'numbers_have': 1 if set_one_numbers & set(obj.numbers)
                        else 0
                    }

        return probability_one_number
