import json
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from lotto_app.constants import RUS_LOTTO_URL, RUS_LOTTO_HEADERS
from lotto_app.app.views.games import GameModelViewSet
from lotto_app.app.models import Game

from lotto_app.app.utils import (
    tickets_from_stoloto,
    get_game_info,
    get_tickets,
    index_bingo,
    index_9_parts
)


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
        five_games_info = GameModelViewSet.get_five_games_info(last_game)
        last_game_info = get_game_info(last_game_obj)
        choice_tickets = self._read_file_json()

        return {'choice_tickets': choice_tickets,
                'first_line_6': set(last_game_info['first_line_6']),
                'first_line_15': set(last_game_info['first_line_15']),
                'last_8_numbers': set(five_games_info['last_8_numbers']),
                'total_cost_numbers': five_games_info['total_cost_numbers']
                }

    def _ticket_validate_line(self, value, data_validate):
        if len(set(value['line_1_1']) & data_validate['first_line_6']) < 3\
                and len(set(value['line_1_2']) & data_validate['first_line_6']) < 3\
                and len(set(value['line_1_3']) & data_validate['first_line_6']) < 3\
                and len(set(value['line_2_1']) & data_validate['first_line_6']) < 3\
                and len(set(value['line_2_2']) & data_validate['first_line_6']) < 3\
                and len(set(value['line_2_3']) & data_validate['first_line_6']) < 3:
            return True
        return False

    def _ticket_validate_cards(self, value, data_validate):
        if len(set(value['card_1']) & data_validate['first_line_15']) < 6\
                and len(set(value['card_2']) & data_validate['first_line_15']) < 6:
            return True
        return False

    def _ticket_9_parts(self, total_cost_numbers, numbers):
        sum_9_parts = index_9_parts(total_cost_numbers, numbers)
        print(sum_9_parts)
        for i in range(0, 9):
            if i not in sum_9_parts:
                return True

        if sum_9_parts[0] not in [3, 4, 5, 6, 7]:
            return True
        if sum_9_parts[1] not in [3, 4, 5, 6, 7]:
            return True
        if sum_9_parts[2] not in [3, 4, 5, 6, 7]:
            return True
        if sum_9_parts[3] not in [2, 3, 4, 5]:
            return True
        if sum_9_parts[4] not in [2, 3, 4, 5]:
            return True
        if sum_9_parts[5] not in [2, 3, 4, 5]:
            return True
        if sum_9_parts[6] not in [2, 3, 4]:
            return True
        if sum_9_parts[7] not in [2, 3, 4]:
            return True
        if sum_9_parts[8] not in [2, 3, 4]:
            return True
        return False

    def _ticket_repeat_numbers(self, choice_tickets, numbers):
        set_numbers = set()
        for ticket, v in choice_tickets.items():
            set_numbers.update(v[1])

        if len(set_numbers & set(numbers)) > 10:
            print('ticket repeat numbers: ', len(set_numbers & set(numbers)))
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

        # if not self._ticket_validate_cards(value, data_validate):
        #     print(f'{num_ticket}: Not validate cards')
        #     return False

        _index = index_bingo(data_validate['total_cost_numbers'], value['numbers'])
        print(_index)
        if _index < 7400 or _index > 8400:
            print(f'{num_ticket}: Not validate _index')
            return False

        # if self._ticket_9_parts(data_validate['total_cost_numbers'], value['numbers']):
        #     print(f'{num_ticket}: Not validate ticket_9_parts')
        #     return False

        if self._ticket_repeat_numbers(data_validate['choice_tickets'], value['numbers']):
            print(f'{num_ticket}: Not validate ticket repeat numbers')
            return False

        print(set(value['numbers']) )

        if len((set(value['numbers']) & {})) <= 9:
            print(f'{num_ticket}: Not validate ticket 1 ... 90')
            return False

        if len((set(value['numbers']) & {})) >= 4:
            print(f'{num_ticket}: Not validate bad numbers')
            return False

        return approved_ticket

    @action(detail=False, url_path='choice_ten_tickets', methods=['get'])
    def choice_ten_tickets(self, request):
        last_game = int(request.query_params.get('game')) - 1
        data_validate = self._get_data_validate(last_game)
        response_json = data_validate['choice_tickets']
        tickets = {}
        for i in range(0, 1500):
            tickets.update(get_tickets(tickets_from_stoloto(RUS_LOTTO_URL, RUS_LOTTO_HEADERS)))

        for t, value in tickets.items():
            if self._ticket_validate(t, value, data_validate):
                _index = index_bingo(data_validate['total_cost_numbers'], value['numbers'])
                v = {t: [_index, value['line_1_1'] + value['line_1_2'][0:2], value['numbers']]}
                response_json.update(v)
                self._write_file_json(response_json)
                data_validate['choice_tickets'].update(v)

        print(last_game)
        return Response(response_json, status=200)