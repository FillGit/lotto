import json
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from lotto_app.constants import RUS_LOTTO_URL, RUS_LOTTO_HEADERS

from lotto_app.app.utils import tickets_from_stoloto, get_tickets

class PcChoiceViewSet(ViewSet):
    file_choice_ten_tickets = 'file_choice_ten_tickets.json'

    def _read_file_json(self):
        try:
            with open(self.file_choice_ten_tickets, "r") as read_file:
                dict_choice = json.load(read_file)
        except FileNotFoundError:
            dict_choice = {}
        return dict_choice

    def _write_file_json(self, dict_choice):
        with open(self.file_choice_ten_tickets, "w") as write_file:
            json.dump(dict_choice, write_file)

    @action(detail=False, url_path='choice_ten_tickets', methods=['get'])
    def choice_ten_tickets(self, request):
        response_json = self._read_file_json()
        for i in range(0, 20):
            response_json.update(tickets_from_stoloto(RUS_LOTTO_URL, RUS_LOTTO_HEADERS))
            self._write_file_json(response_json)
        return Response(response_json, status=200)