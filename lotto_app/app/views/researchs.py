from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game


class ResearchViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('game')

    @action(detail=True, url_path='combination_comparisons', methods=['get'])
    def combination_comparisons(self, request, pk=None):
        main_game_obj = self.queryset.get(game=pk)

        main_list_win_numbers = main_game_obj.get_game_numbers()[:60]
        dict_common_numbers = {}

        for _obj in self.queryset:
            if _obj.game != pk:
                _comparison_list_win_numbers = _obj.get_game_numbers()[:60]
                set_common_numbers = set(main_list_win_numbers) & set(_comparison_list_win_numbers)
                dict_common_numbers.update({_obj.game: [len(set_common_numbers), sorted(list(set_common_numbers))]})

        resp = {'combination_comparisons': pk}
        resp.update(dict(sorted(dict_common_numbers.items(), key=lambda item: item[1], reverse=True)))
        return Response(resp, status=200)
