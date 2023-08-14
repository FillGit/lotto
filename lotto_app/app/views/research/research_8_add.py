from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.commands.command_utils import CombinationOptions8Add, InfoSequence8Add
from lotto_app.app.views.research.research import ResearchViewSet


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
        only_len_sequence = int(request.query_params.get('only_len_sequence', 0))
        i_s = InfoSequence8Add(ng, game_start, how_games)
        all_info_sequence = i_s.get_all_info_sequence(sequence, only_len_sequence)
        all_info_sequence.append(i_s.get_info_difference(all_info_sequence))
        return Response(all_info_sequence, status=200)
