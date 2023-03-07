from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game, LottoTickets


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
