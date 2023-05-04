from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game, LottoTickets
from lotto_app.app.utils import get_game_info, index_9_parts
from lotto_app.app.views.games import GameViewSet


class ResearchViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Game.objects.filter(name_game=self.kwargs['ng']).order_by('game_id')

    def get_game_obj(self):
        return Game.objects.get(game_id=self.kwargs['pk'])

    @action(detail=True, url_path='comparison_win_ticket', methods=['get'])
    def comparison_win_ticket(self, request, ng, pk=None):
        main_game_obj = self.get_queryset().get(game_id=pk)

        main_list_win_numbers = main_game_obj.numbers[:60]
        dict_common_numbers = {}

        for _obj in self.get_queryset():
            if _obj.game_id != pk:
                _comparison_list_win_numbers = _obj.numbers[:60]
                set_common_numbers = set(main_list_win_numbers) & set(_comparison_list_win_numbers)
                dict_common_numbers.update({_obj.game_id: [len(set_common_numbers), sorted(list(set_common_numbers))]})

        resp = {'main_game': pk}
        resp.update(dict(sorted(dict_common_numbers.items(), key=lambda item: item[1], reverse=True)))
        return Response(resp, status=200)

    @action(detail=True, url_path='search_win_ticket', methods=['get'])
    def search_win_ticket(self, request, ng, pk=None):
        last_win_number_ticket = int(request.query_params.get('last_win_number_ticket', None))
        main_game_obj = self.get_queryset().get(game_id=pk)
        main_set_win_numbers = {int(num) for num in main_game_obj.get_win_list(last_win_number_ticket)}

        ticket_ids = []
        for ticket_obj in LottoTickets.objects.filter(game_obj=self.get_game_obj()):
            ticket_set_numbers = set(ticket_obj.get_ticket_numbers())
            set_n = len(ticket_set_numbers - main_set_win_numbers)
            if set_n == 0:
                ticket_ids.append(ticket_obj.ticket_id)
        return Response(ticket_ids, status=200)

    @action(detail=True, url_path='games_no_numbers', methods=['get'])
    def games_no_numbers(self, request, ng, pk):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        if not game_start:
            return Response({"error": "query_params doesn't game_start"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not how_games:
            return Response({"error": "query_params doesn't how_games"},
                            status=status.HTTP_400_BAD_REQUEST)

        game_objs = Game.objects.filter(
            name_game=ng,
            last_win_number_card__isnull=False,
            last_win_number_ticket__isnull=False
        ).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        ).filter(game_id_int__lte=game_start, game_id_int__gte=game_start-how_games-5
                 ).order_by('-game_id_int')[0:how_games]

        if pk not in [game_obj.game_id for game_obj in game_objs]:
            return Response({"error": f"game_id - {game_start} doesn't have in query"},
                            status=status.HTTP_400_BAD_REQUEST)

        dict_no_numbers = {}
        game_index_9_parts = {}
        for game_obj in game_objs:
            game_id = int(game_obj.game_id)
            total_cost_numbers = GameViewSet.get_several_games_info(ng, game_id)['total_cost_numbers']
            game_info = get_game_info(game_obj)
            dict_no_numbers[game_id] = GameViewSet.get_several_games_no_numbers(
                total_cost_numbers, game_info)
            game_index_9_parts[game_id] = index_9_parts(total_cost_numbers,
                                                        dict_no_numbers[game_id].keys())
            dict_no_numbers[game_id]['no_numbers_9_parts'] = game_index_9_parts[game_id]

        dict_no_numbers['all_no_numbers_9_parts'] = {}
        for _game, _index_9_parts in game_index_9_parts.items():
            for part, cost in _index_9_parts.items():
                if part not in dict_no_numbers['all_no_numbers_9_parts']:
                    dict_no_numbers['all_no_numbers_9_parts'][part] = cost
                else:
                    dict_no_numbers['all_no_numbers_9_parts'][part] += cost
            dict_no_numbers['all_no_numbers_9_parts'] = dict(
                sorted(dict_no_numbers['all_no_numbers_9_parts'].items(), key=lambda item: item[1]))
        return Response(dict_no_numbers, status=200)
