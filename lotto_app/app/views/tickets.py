from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from lotto_app.constants import RUS_LOTTO_URL, RUS_LOTTO_HEADERS

from lotto_app.app.utils import tickets_from_stoloto, tickets_check_status_code, get_tickets

class TicketViewSet(ViewSet):

    @action(detail=False, url_path='rus_tickets_from_stoloto', methods=['get'])
    def rus_tickets_from_stoloto(self, request):
        response = tickets_from_stoloto(RUS_LOTTO_URL, RUS_LOTTO_HEADERS)
        return Response(response.json(), status=response.status_code)

    @action(detail=False, url_path='dict_tickets', methods=['get'])
    def dict_tickets(self, request):
        response = tickets_from_stoloto(RUS_LOTTO_URL, RUS_LOTTO_HEADERS)
        response_json = tickets_check_status_code(response)
        tickets = get_tickets(response_json)
        return Response(tickets, status=200)
