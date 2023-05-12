import requests
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import LottoTickets
from lotto_app.app.serializers import LottoTicketsSerializer
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
        return LottoTickets.objects.get(game_id=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        name_game = self.kwargs['ng']
        game_id = request.data['game_id']
        lotto_tickets = []
        tickets_from_remote_server = {}
        _ticket_ids = [ticket_obj.ticket_id for ticket_obj in self.lotto_tickets_by_game_objs(game_id)]

        for i in range(1, QUANTITY_TICKETS):
            for ticket_id, val in self._get_tickets_from_json(self.LOTTO_URL, self.LOTTO_HEADERS).items():
                if ticket_id not in _ticket_ids:
                    tickets_from_remote_server[ticket_id] = val
                _ticket_ids.append(ticket_id)

        for ticket, v in tickets_from_remote_server.items():

            lotto_tickets.append(LottoTickets(name_game=name_game,
                                              game_id=game_id,
                                              ticket_id=ticket,
                                              first_seven_numbers=v['numbers'][0:7],
                                              ticket_numbers=v['numbers']))
        try:
            LottoTickets.objects.bulk_create(lotto_tickets)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        return Response([], status=status.HTTP_201_CREATED)

    def lotto_tickets_by_game_objs(self, game_id=None):
        name_game = self.kwargs['ng']
        if not game_id:
            game_id = self.kwargs['pk']
        return LottoTickets.objects.filter(name_game=name_game, game_id=game_id)

    def destroy(self, request, *args, **kwargs):
        self.lotto_tickets_by_game_objs().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='tickets_from_server', methods=['get'])
    def tickets_from_server(self, request):
        resp = requests.get(self.LOTTO_URL, headers=self.LOTTO_HEADERS)
        return Response(resp.json(), status=200)

    @action(detail=True, url_path='count', methods=['get'])
    def count(self, request, **kwargs):
        return Response(self.lotto_tickets_by_game_objs().count(), status=200)

    @action(detail=True, url_path='ticket', methods=['get'])
    def ticket(self, request, **kwargs):
        ticket_obj = self.lotto_tickets_by_game_objs().get(ticket_id=request.query_params.get('ticket_id'))
        serializer = self.get_serializer(ticket_obj)
        return Response(serializer.data)
