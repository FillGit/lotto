from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game, LottoTickets
from lotto_app.app.utils import get_game_info, index_9_parts
from lotto_app.app.views.games import GameViewSet


class ResearchViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('game')

    def get_game_obj(self):
        return Game.objects.get(game=self.kwargs['pk'])

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

    @action(detail=True, url_path='search_win_ticket', methods=['get'])
    def search_win_ticket(self, request, pk=None):
        last_win_number_ticket = int(request.query_params.get('last_win_number_ticket', None))
        main_game_obj = self.queryset.get(game=pk)
        main_set_win_numbers = {int(num) for num in main_game_obj.get_win_list(last_win_number_ticket)}

        ticket_ids = []
        for ticket_obj in LottoTickets.objects.filter(game_obj=self.get_game_obj()):
            ticket_set_numbers = set(ticket_obj.get_ticket_numbers())
            set_n = len(ticket_set_numbers - main_set_win_numbers)
            if set_n == 0:
                ticket_ids.append(ticket_obj.ticket_id)
        return Response(ticket_ids, status=200)

    @action(detail=False, url_path='games_no_numbers', methods=['get'])
    def games_no_numbers(self, request):
        game_start = int(request.query_params.get('game_start', 0))
        game_end = int(request.query_params.get('game_end', 0))

        if not game_start:
            return Response({"error": "query_params doesn't game_start"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not game_end:
            return Response({"error": "query_params doesn't game_end"},
                            status=status.HTTP_400_BAD_REQUEST)

        game_objs = Game.objects.filter(game__in=[g for g in range(game_start, game_end+1)])
        dict_no_numbers = {}
        game_index_9_parts = {}
        for game_obj in game_objs:
            game = game_obj.game
            last_total_cost_numbers = GameViewSet.get_last_games_info(int(game) - 1)['total_cost_numbers']
            game_info = get_game_info(game_obj)
            dict_no_numbers[game] = GameViewSet.get_five_games_no_numbers(last_total_cost_numbers, game_info)
            game_index_9_parts[game] = index_9_parts(last_total_cost_numbers,
                                                     dict_no_numbers[game].keys())
            dict_no_numbers[game]['_index_9_parts'] = game_index_9_parts[game]

        dict_no_numbers['all_games_index_9_parts'] = {}
        for _game, _index_9_parts in game_index_9_parts.items():
            for part, cost in _index_9_parts.items():
                if part not in dict_no_numbers['all_games_index_9_parts']:
                    dict_no_numbers['all_games_index_9_parts'][part] = cost
                else:
                    dict_no_numbers['all_games_index_9_parts'][part] += cost
            dict_no_numbers['all_games_index_9_parts'] = dict(
                sorted(dict_no_numbers['all_games_index_9_parts'].items(), key=lambda item: item[1]))
        return Response(dict_no_numbers, status=200)
