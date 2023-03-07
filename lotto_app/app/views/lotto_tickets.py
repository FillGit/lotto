import requests
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game, LottoTickets
from lotto_app.app.serializers import LottoTicketsSerializer
from lotto_app.app.utils import get_str_numbers
from lotto_app.config import get_from_config, get_section_from_config
from lotto_app.constants import QUANTITY_TICKETS


class LottoTicketsViewSet(viewsets.ModelViewSet):
    queryset = LottoTickets.objects.all()
    serializer_class = LottoTicketsSerializer
    LOTTO_URL = get_from_config('lotto_url', 'url')
    LOTTO_HEADERS = get_section_from_config('lotto_headers')

    def _get_tickets_from_json(self, url, headers):
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise ValueError(f'{response.status_code} and {response.json()}')
        return {t['barCode']: {'numbers': t['numbers']} for t in response.json()['tickets']}

    def get_object(self):
        return LottoTickets.objects.get(game=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        game_obj = Game.objects.get(game=request.data['game'])
        lotto_tickets = []
        tickets_from_remote_server = {}
        _ticket_ids = [ticket_obj.ticket_id for ticket_obj in self.lotto_tickets_by_game_objs(request.data['game'])]

        for i in range(1, QUANTITY_TICKETS):
            for ticket_id, val in self._get_tickets_from_json(self.LOTTO_URL, self.LOTTO_HEADERS).items():
                if ticket_id not in _ticket_ids:
                    tickets_from_remote_server[ticket_id] = val
                _ticket_ids.append(ticket_id)

        for ticket, v in tickets_from_remote_server.items():
            lotto_tickets.append(LottoTickets(game_obj=game_obj,
                                              ticket_id=ticket,
                                              first_seven_numbers=get_str_numbers(v['numbers'][0:7]),
                                              ticket_numbers=get_str_numbers(v['numbers'])))
        try:
            LottoTickets.objects.bulk_create(lotto_tickets)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        return Response([], status=status.HTTP_201_CREATED)

    def lotto_tickets_by_game_objs(self, game):
        return LottoTickets.objects.filter(game_obj__game=game)

    def destroy(self, request, *args, **kwargs):
        self.lotto_tickets_by_game_objs(kwargs['pk']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='tickets_from_server', methods=['get'])
    def tickets_from_server(self, request):
        resp = requests.get(self.LOTTO_URL, headers=self.LOTTO_HEADERS)
        return Response(resp.json(), status=200)
