from rest_framework import status, viewsets
from rest_framework.response import Response

from lotto_app.app.models import Game, LottoTickets
from lotto_app.app.serializers import LottoTicketsSerializer
from lotto_app.app.utils import get_tickets, tickets_from_stoloto
from lotto_app.config import get_from_config, get_section_from_config
from lotto_app.constants import QUANTITY_TICKETS


class LottoTicketsViewSet(viewsets.ModelViewSet):
    queryset = LottoTickets.objects.all()
    serializer_class = LottoTicketsSerializer
    LOTTO_URL = get_from_config('lotto_url', 'url')
    LOTTO_HEADERS = get_section_from_config('lotto_headers')

    def get_object(self):
        return LottoTickets.objects.get(game=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        game_obj = Game.objects.get(game=request.data['game'])
        lotto_tickets = []
        tickets_from_remote_server = {}

        for i in range(1, QUANTITY_TICKETS):
            tickets_from_remote_server.update(
                get_tickets(tickets_from_stoloto(self.LOTTO_URL, self.LOTTO_HEADERS)))

        for ticket, v in tickets_from_remote_server.items():
            lotto_tickets.append(LottoTickets(game_obj=game_obj,
                                              ticket_number=ticket,
                                              first_seven_numbers=v['numbers'][0:7],
                                              ticket_all_numbers=v['numbers']))
        try:
            LottoTickets.objects.bulk_create(lotto_tickets)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        return Response([], status=status.HTTP_201_CREATED)

    def get_state_number_objs(self):
        return LottoTickets.objects.filter(game_obj__game=self.kwargs['pk'])

    def destroy(self, request, *args, **kwargs):
        self.get_state_number_objs().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
