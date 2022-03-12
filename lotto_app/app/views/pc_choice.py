from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lotto_app.app.utils import tickets_from_stoloto, tickets_check_status_code, get_tickets

class PcChoiceViewSet(ViewSet):
    url = 'https://www.stoloto.ru/p/api/mobile/api/v34/games/change?game=ruslotto&count=20'

    @action(detail=False, url_path='choice_ten_tickets', methods=['get'])
    def choice_ten_tickets(self, request):
        response = tickets_from_stoloto(self.url, headers=self._get_headers())
        return Response(response.json(), status=response.status_code)