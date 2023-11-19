from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.management.command_utils import (
    CombinationOptions8Add,
    InfoSequence8Add,
    Probabilities8Add,
    Probabilities8AddOneNumber
)
from lotto_app.app.utils import str_to_list_of_int
from lotto_app.app.views.research.research import ResearchViewSet
from lotto_app.constants import COMBINATION_OPTIONS_8_ADD


class Research8AddViewSet(ResearchViewSet):

    @action(detail=True, url_path='comparison_all_numbers', methods=['get'])
    def comparison_all_numbers(self, request, ng, pk=None):
        main_game_obj = self.get_game_obj()

        main_list_win_numbers = main_game_obj.numbers[:60]
        dict_common_numbers = {}

        for _obj in self.get_queryset():
            if _obj.game_id != pk:
                set_common_numbers = set(main_list_win_numbers) & set(_obj.numbers)
                dict_common_numbers.update({_obj.game_id: [len(set_common_numbers), sorted(list(set_common_numbers))]})

        resp = {'main_game': pk}
        resp.update(dict(sorted(dict_common_numbers.items(), key=lambda item: item[1], reverse=True)))
        return Response(resp, status=200)

    @action(detail=True, url_path='combination_options', methods=['get'])
    def combination_options(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        combination_options = CombinationOptions8Add(ng, game_start, how_games)
        game_combinations = combination_options.get_game_combinations()
        game_combinations.update(combination_options.get_sum_combination_options(game_combinations))
        return Response(game_combinations, status=200)

    @action(detail=True, url_path='info_sequence', methods=['get'])
    def info_sequence(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        sequence = [int(sequence) for sequence in request.query_params.get('sequence').replace(' ', '').split(',')]
        only_len_sequence = True if int(request.query_params.get('only_len_sequence', 0)) else False
        how_info_games = int(request.query_params.get('how_info_games', 0))
        i_s = InfoSequence8Add(ng, game_start, how_games)
        if not i_s.validate_sequence(sequence):
            return Response({"error": "your sequence didn't pass validate."},
                            status=status.HTTP_400_BAD_REQUEST)

        all_info_sequence = i_s.get_all_info_sequence(sequence, only_len_sequence, how_info_games)
        all_info_sequence.append(i_s.get_info_difference(all_info_sequence))
        return Response(all_info_sequence, status=200)

    @action(detail=True, url_path='all_sequences_in_games', methods=['get'])
    def all_sequences_in_games(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        part_consists_of = int(request.query_params.get('part_consists_of', 1))
        how_info_games = int(request.query_params.get('how_info_games', 0))
        i_s = InfoSequence8Add(ng, game_start, how_games)
        all_sequences_in_games = i_s.get_all_sequences_in_games(part_consists_of, how_info_games)
        return Response(all_sequences_in_games, status=200)

    @action(detail=True, url_path='probability_sequences', methods=['get'])
    def probability_sequences(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        part_consists_of = int(request.query_params.get('part_consists_of'))
        steps_back_games = int(request.query_params.get('steps_back_games'))
        limit_overlap = int(request.query_params.get('limit_overlap'))
        limit_amount_seq = int(request.query_params.get('limit_amount_seq'))
        game_end = game_start - how_games

        probability_sequences = {}
        gen_probability = Probabilities8Add(ng, game_start, how_games + steps_back_games)
        for obj in gen_probability.game_objs:
            if int(obj.game_id) > game_end:
                _id = int(obj.game_id)-1
                exceeding_limit_overlap, game_objs = gen_probability.get_exceeding_limit_overlap(
                    ng, _id,
                    part_consists_of, steps_back_games,
                    limit_overlap, gen_probability
                )

                if exceeding_limit_overlap and len(exceeding_limit_overlap.keys()) >= limit_amount_seq:
                    probability_sequences[obj.game_id] = {
                        'ids': [_obj.game_id for _obj in game_objs],
                        'exceeding_limit_overlap': exceeding_limit_overlap,
                        'numbers_have': [
                            seq for seq in exceeding_limit_overlap
                            if set(str_to_list_of_int(seq)).issubset(set(obj.numbers))
                        ]}

        probability_sequences.update({
            'check_games': how_games,
            'exceeding_limit_overlap': len(probability_sequences),
            'numbers_have': len([v['numbers_have']
                                 for k, v in probability_sequences.items() if v['numbers_have']])
        })
        return Response(probability_sequences, status=200)

    @action(detail=True, url_path='probability_one_number', methods=['get'])
    def probability_one_number(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        steps_back_games_previous = int(request.query_params.get('steps_back_games_previous'))
        steps_back_games_small = int(request.query_params.get('steps_back_games_small'))
        steps_back_games_big = int(request.query_params.get('steps_back_games_big'))

        probability_one_number = Probabilities8AddOneNumber().probability_one_number(
            ng, game_start, how_games,
            steps_back_games_previous,
            steps_back_games_small,
            steps_back_games_big
        )
        numbers_have = len([v['numbers_have']
                            for k, v in probability_one_number.items() if v['numbers_have']])

        probability_one_number.update({
            'check_games': how_games,
            'len_set_one_numbers': len(probability_one_number),
            'numbers_have': numbers_have,
            'probability': numbers_have/len(probability_one_number) if len(probability_one_number) > 0 else 0,
        })
        return Response(probability_one_number, status=200)

    @action(detail=True, url_path='comparison_last_game', methods=['get'])
    def comparison_last_game(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))

        gen_probability = Probabilities8Add(ng, game_start, how_games)
        comparison_last_game = gen_probability.get_comparison_last_game(gen_probability)
        sum_comparison_last_game = {k: 0 for k in range(0, 9)}
        for k in range(0, 9):
            for _, same_numbers in comparison_last_game.items():
                if same_numbers == k:
                    sum_comparison_last_game[k] += 1
        comparison_last_game.update(sum_comparison_last_game)
        return Response(comparison_last_game, status=200)

    @action(detail=True, url_path='favorite_option', methods=['get'])
    def favorite_option(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games'))
        steps_back_games = int(request.query_params.get('steps_back_games', 0))
        favorite_option = str(request.query_params.get('favorite_option', ''))
        values_from_max_list = int(request.query_params.get('values_from_max_list', 2))

        gen_probability = Probabilities8Add(ng, game_start, how_games)
        count_game_numbers = 0
        _numbers = [n for n in range(1, gen_probability.numbers_in_lotto + 1)]

        for obj in gen_probability.game_objs:
            max_numbers_in_games = []
            if steps_back_games:
                max_numbers_in_games = gen_probability.get_max_numbers_in_games(ng, int(obj.game_id) - 1,
                                                                                steps_back_games,
                                                                                gen_probability)[0:values_from_max_list]
            if favorite_option:
                set_future_numbers = set(gen_probability.get_favorite_option(favorite_option,
                                                                             max_numbers=max_numbers_in_games))
            else:
                set_future_numbers = set(gen_probability.get_shuffle_numbers(_numbers, max_numbers_in_games))

            common_numbers = set(obj.numbers) & set_future_numbers
            print(obj.game_id, len(common_numbers), len(set(obj.numbers) & set(max_numbers_in_games)))
            if len(common_numbers) >= 5:
                count_game_numbers += len(common_numbers)

        return Response({'favorite_option': favorite_option,
                         'count_game_numbers': count_game_numbers},
                        status=200)

    @action(detail=True, url_path='maximum_numbers_in_games', methods=['get'])
    def maximum_numbers_in_games(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games'))
        gen_probability = Probabilities8Add(ng, game_start, how_games)
        maximum_numbers_in_games = gen_probability.get_max_numbers_in_games(ng, game_start,
                                                                            how_games,
                                                                            gen_probability)
        return Response(maximum_numbers_in_games,
                        status=200)

    def _add_probability(self, gen_outcomes, elementary_outcomes):
        if elementary_outcomes:
            return elementary_outcomes/gen_outcomes
        return 0

    @action(detail=True, url_path='search_needed_combinations', methods=['get'])
    def search_needed_combinations(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games'))
        name_sequence = str(request.query_params.get('name_sequence'))
        steps_back_games = int(request.query_params.get('steps_back_games'))
        steps_back_co = int(request.query_params.get('steps_back_combination_option', 0))
        probabilities = Probabilities8Add(ng, game_start, how_games)
        needed_combinations = probabilities.get_search_needed_combinations(name_sequence,
                                                                           steps_back_games,
                                                                           steps_back_co)
        len_needed_combinations = len(needed_combinations)
        needed_combinations.append({
            'needed_combinations': len_needed_combinations,
            'probability_1': self._add_probability(
                len_needed_combinations,
                len([comb for comb in needed_combinations
                     if list(comb.values())[0] == COMBINATION_OPTIONS_8_ADD[name_sequence]]
                    )),
            'probability_2': self._add_probability(
                len_needed_combinations,
                len([comb for comb in needed_combinations
                     if list(comb.values())[0][0] < 3]
                    ))})
        return Response(needed_combinations, status=200)
