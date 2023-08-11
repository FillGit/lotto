from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.commands.command_utils import CombinationOptions8Add
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
        return Response(CombinationOptions8Add(ng,
                                               game_start,
                                               how_games).get_combination_options(),
                        status=200)
