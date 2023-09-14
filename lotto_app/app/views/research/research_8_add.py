from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.commands.command_utils import CombinationOptions8Add, InfoSequence8Add, Probabilities8Add
from lotto_app.app.utils import str_to_list_of_int
from lotto_app.app.views.research.research import ResearchViewSet
from statistics import mean


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

    def _get_probability_objs(self, game_id, steps_back_games, gen_objs):
        ids = [str(_id) for _id in range(int(game_id), int(game_id) - steps_back_games, -1)]
        return [obj for obj in gen_objs if obj.game_id in ids]

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
                _p8add = Probabilities8Add(
                    ng, _id, steps_back_games,
                    game_objs=self._get_probability_objs(_id, steps_back_games, gen_probability.game_objs)
                )
                exceeding_limit_overlap = _p8add.get_count_sequences(part_consists_of, steps_back_games, limit_overlap)
                if exceeding_limit_overlap and len(exceeding_limit_overlap.keys()) >= limit_amount_seq:
                    probability_sequences[obj.game_id] = {
                        'ids': [_obj.game_id for _obj in _p8add.game_objs],
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

    def _get_min_number(self, all_sequences_in_games):
        return str_to_list_of_int(min(all_sequences_in_games,
                                      key=all_sequences_in_games.get))[0]

    def _get_middle_sum(self, all_sequences_in_games):
        list_sum = []
        for str_number, sum in all_sequences_in_games.items():
            list_sum.append(sum)
        return mean(list_sum)

    def _probability_one_number_condition(self, min_number, sequences_small, game_objs):
        print(min_number, game_objs[0].numbers, game_objs[1].numbers, self._get_middle_sum(sequences_small))
        if min_number in game_objs[0].numbers and min_number in game_objs[1].numbers and (
            sequences_small[f'[{min_number}]'] < self._get_middle_sum(sequences_small)
        ):
            return True
        return False

    @action(detail=True, url_path='probability_one_number', methods=['get'])
    def probability_one_number(self, request, ng, pk=None):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        steps_back_games_small = int(request.query_params.get('steps_back_games_small'))
        steps_back_games_big = int(request.query_params.get('steps_back_games_big'))
        game_end = game_start - how_games

        probability_one_number = {}
        gen_probability = Probabilities8Add(ng, game_start, how_games + steps_back_games_big)
        for obj in gen_probability.game_objs:
            if int(obj.game_id) > game_end:
                _id = int(obj.game_id)-1
                i_s = InfoSequence8Add(ng, _id, steps_back_games_big,
                                       game_objs=self._get_probability_objs(_id, steps_back_games_big,
                                                                            gen_probability.game_objs))
                sequences_small = i_s.get_all_sequences_in_games(1, steps_back_games_small)
                sequences_big = i_s.get_all_sequences_in_games(1, steps_back_games_big)
                min_number = self._get_min_number(sequences_big)

                if self._probability_one_number_condition(min_number,
                                                          sequences_small,
                                                          i_s.game_objs):
                    probability_one_number[obj.game_id] = {
                        # 'ids': [_obj.game_id for _obj in i_s.game_objs],
                        'min_number': {min_number: sequences_small[f'[{min_number}]']},
                        'numbers_have': 1 if min_number in obj.numbers else 0
                    }
        numbers_have = len([v['numbers_have']
                            for k, v in probability_one_number.items() if v['numbers_have']])
        probability_one_number.update({
            'check_games': how_games,
            'max_number': len(probability_one_number),
            'numbers_have': numbers_have,
            'probability': numbers_have/len(probability_one_number)
        })
        return Response(probability_one_number, status=200)
