import json
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from lotto_app.constants import RUS_LOTTO_URL, RUS_LOTTO_HEADERS
from lotto_app.app.views.games import GameModelViewSet
from lotto_app.app.models import Game

from lotto_app.app.utils import tickets_from_stoloto, get_game_info, get_first_cell, get_tickets

class PcChoiceViewSet(ViewSet):
    file_choice_ten_tickets = 'file_choice_ten_tickets.json'

    def _read_file_json(self):
        try:
            with open(self.file_choice_ten_tickets, "r") as read_file:
                choice_tickets = json.load(read_file)
        except FileNotFoundError:
            choice_tickets = {}
        return choice_tickets

    def _write_file_json(self, dict_choice):
        with open(self.file_choice_ten_tickets, "w") as write_file:
            json.dump(dict_choice, write_file)

    def _get_data_validate(self, last_game):
        last_game_obj = Game.objects.get(game=last_game)
        three_games_info = GameModelViewSet.get_three_games_info(last_game)
        last_game_info = get_game_info(last_game_obj)
        choice_tickets = self._read_file_json()

        return {'choice_tickets': choice_tickets,
                'first_line_6': set(last_game_info['first_line_6']),
                'last_8_numbers': set(three_games_info['last_8_numbers']),
                'three_18_cell': set(three_games_info['three_18_cell']),
                'three_30_cell': set(three_games_info['three_30_cell']),
                }

    def _ticket_validate_line(self, value, data_validate):
        if len(set(value['line_1_1']) & data_validate['first_line_6']) < 2\
                and len(set(value['line_1_2']) & data_validate['first_line_6']) < 2\
                and len(set(value['line_1_3']) & data_validate['first_line_6']) < 2\
                and len(set(value['line_2_1']) & data_validate['first_line_6']) < 2\
                and len(set(value['line_2_2']) & data_validate['first_line_6']) < 2\
                and len(set(value['line_2_3']) & data_validate['first_line_6']) < 2:
            return True
        return False

    def _ticket_validate_cards(self, value, data_validate):
        if len(set(value['card_1']) & data_validate['three_18_cell']) < 6\
                and len(set(value['card_2']) & data_validate['three_18_cell']) < 6:
            return True
        return False

    def _ticket_validate(self, num_ticket, value, data_validate):
        approved_ticket = num_ticket

        if num_ticket in data_validate['choice_tickets']:
            print(f'{num_ticket}: Not validate choice_tickets')
            return False
        if not self._ticket_validate_line(value, data_validate):
            print(f'{num_ticket}: Not validate first_line_6')
            return False

        if not self._ticket_validate_cards(value, data_validate):
            print(f'{num_ticket}: Not validate cards')
            return False

        if len(set(value['numbers']) & data_validate['last_8_numbers']) > 2:
            print(f'{num_ticket}: Not validate last_8_numbers')
            return False

        if len(set(value['numbers']) & data_validate['three_30_cell']) < 19:
            print(data_validate['three_30_cell'])
            print(len(set(value['numbers']) & data_validate['three_30_cell']))
            print(f'{num_ticket}: Not validate three_30_cell')
            return False
        return approved_ticket

    @action(detail=False, url_path='choice_ten_tickets', methods=['get'])
    def choice_ten_tickets(self, request):
        last_game = int(request.query_params.get('game')) - 1
        data_validate = self._get_data_validate(last_game)
        response_json = data_validate['choice_tickets']
        tickets = {}
        for i in range(0, 1000):
            tickets.update(get_tickets(tickets_from_stoloto(RUS_LOTTO_URL, RUS_LOTTO_HEADERS)))

        for t, value in tickets.items():
            approved_ticket = self._ticket_validate(t, value, data_validate)
            if approved_ticket:
                v = {t: value['line_1_1'] + value['line_1_2'][0:2]}
                response_json.update(v)
                self._write_file_json(response_json)
                data_validate['choice_tickets'].update(v)
        print(last_game)
        print(data_validate['three_30_cell'])
        return Response(response_json, status=200)