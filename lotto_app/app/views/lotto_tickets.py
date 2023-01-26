from rest_framework import viewsets, status
from rest_framework.response import Response

from lotto_app.app.serializers import LottoTicketsSerializer
from lotto_app.app.models import Game, LottoTickets

from lotto_app.constants import LOTTO_URL, LOTTO_HEADERS, QUANTITY_TICKETS

from lotto_app.app.utils import tickets_from_stoloto, get_tickets


class LottoTicketsViewSet(viewsets.ModelViewSet):
    queryset = LottoTickets.objects.all()
    serializer_class = LottoTicketsSerializer

    def get_object(self):
        return LottoTickets.objects.get(game=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        game_obj = Game.objects.get(game=request.data['game'])
        lotto_tickets = []
        tickets_from_remote_server = {}

        for i in range(1, QUANTITY_TICKETS):
            tickets_from_remote_server.update(get_tickets(tickets_from_stoloto(LOTTO_URL, LOTTO_HEADERS)))

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
