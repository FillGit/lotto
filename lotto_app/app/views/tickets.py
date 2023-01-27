from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lotto_app.app.utils import get_tickets, tickets_from_stoloto
from lotto_app.config import get_from_config, get_section_from_config

LOTTO_URL = get_from_config('lotto_url', 'url')
LOTTO_HEADERS = get_section_from_config('lotto_headers')

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
