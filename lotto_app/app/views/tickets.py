from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from lotto_app.constants import LOTTO_URL, LOTTO_HEADERS

from lotto_app.app.utils import tickets_from_stoloto, get_tickets

class TicketViewSet(ViewSet):

    @action(detail=False, url_path='rus_tickets_from_stoloto', methods=['get'])
    def rus_tickets_from_stoloto(self, request):
        response_json = tickets_from_stoloto(LOTTO_URL, LOTTO_HEADERS)
        return Response(response_json, status=200)

    @action(detail=False, url_path='dict_tickets', methods=['get'])
    def dict_tickets(self, request):
        response_json = tickets_from_stoloto(LOTTO_URL, LOTTO_HEADERS)
        tickets = get_tickets(response_json)
        return Response(tickets, status=200)
