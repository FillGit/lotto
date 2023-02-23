from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game
from lotto_app.app.serializers import GameSerializer
from lotto_app.app.utils import get_game_info, index_9_parts, index_bingo


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('game')
    serializer_class = GameSerializer

    def get_object(self):
        return Game.objects.get(game=self.kwargs['pk'])

    def game_request(self, request):
        game = request.query_params.get('game')
        return game, Game.objects.get(game=game)

    @staticmethod
    def get_five_games_info(game):
        all_cost_numbers = {}
        all_info = [get_game_info(Game.objects.get(game=game), 1.4),
                    get_game_info(Game.objects.get(game=int(game) - 1), 1.3),
                    get_game_info(Game.objects.get(game=int(game) - 2), 1.2),
                    get_game_info(Game.objects.get(game=int(game) - 3), 1.1),
                    get_game_info(Game.objects.get(game=int(game) - 4), 1.0),
                    ]

        for num in range(1, 91):
            snum = str(num)
            all_cost_numbers[num] = sum(
                [all_info[i]['cost_numbers'][snum] for i in range(0, 5)])

        total_cost_numbers = dict((x, y) for x, y in sorted(all_cost_numbers.items(),
                                                            key=lambda x: x[1]))
        str_total_cost_numbers = [{k: y} for k, y in total_cost_numbers.items()]
        return {
            'min_cost': str_total_cost_numbers[0],
            'max_cost': str_total_cost_numbers[89],
            'last_8_numbers': [list(num.keys())[0] for num in str_total_cost_numbers[-17:]],
            'total_cost_numbers': total_cost_numbers,
            'total_index_bingo_30': index_bingo(total_cost_numbers,
                                                [num for num in list(total_cost_numbers.keys())[0:30]])
        }

    @action(detail=False, url_path='info', methods=['get'])
    def info(self, request):
        print('info/')
        game, game_obj = self.game_request(request)
        return Response(get_game_info(game_obj), status=200)

    @action(detail=False, url_path='five_games_info', methods=['get'])
    def five_games_info(self, request):
        print('five_games_info/')
        game = request.query_params.get('game')
        return Response(self.get_five_games_info(game), status=200)

    def _condition_numbers(self, how_many, previous_games, current_game, condition):
        return {int(num) for num, value in self._value_previous_games(how_many, previous_games, current_game).items()
                if value == condition}

    def _get_good_numbers(self, current_game):
        good_numbers = self._condition_numbers(45, 5, current_game, 0)
        good_numbers.update(self._condition_numbers(40, 5, current_game, 0))
        good_numbers.update(self._condition_numbers(45, 3, current_game, 0))
        good_numbers.update(self._condition_numbers(40, 3, current_game, 0))
        return good_numbers

    def _get_bad_numbers(self, current_game):
        bad_numbers = self._condition_numbers(45, 5, current_game, 5)
        bad_numbers.update(self._condition_numbers(40, 5, current_game, 5))
        bad_numbers.update(self._condition_numbers(45, 5, current_game, 4))
        bad_numbers.update(self._condition_numbers(45, 3, current_game, 3))
        bad_numbers.update(self._condition_numbers(40, 3, current_game, 3))
        return bad_numbers

    @action(detail=False, url_path='index_bingo_30', methods=['get'])
    def index_bingo_30(self, request):
        print('index_bingo_30/')
        game, game_obj = self.game_request(request)
        last_total_cost_numbers = self.get_five_games_info(int(game) - 1)['total_cost_numbers']
        game_info = get_game_info(game_obj)
        null_numbers = {num: last_total_cost_numbers[int(num)] for num, v in game_info['cost_numbers'].items() if
                        v == 0}
        indexes = {
            'index_bingo': index_bingo(last_total_cost_numbers, game_info['bingo_30']),
            'index_9_parts': index_9_parts(last_total_cost_numbers, game_info['bingo_30']),
            'good_numbers': self._get_good_numbers(int(game)),
            'bad_numbers': self._get_bad_numbers(int(game)),
            'null_numbers': null_numbers,
        }
        return Response(indexes, status=200)

    def _value_previous_games(self, how_many, previous_games, current_game):
        value_previous_games = {str(i): 0 for i in range(1, 91)}
        number_info = []
        for game in range(current_game - previous_games + 1, current_game + 1):
            print(game)
            number_info.append(get_game_info(Game.objects.get(game=int(game)))['numbers'][:how_many])

        for _info in number_info:
            for num in _info:
                value_previous_games[num] += 1
        return value_previous_games

    @action(detail=False, url_path='value_previous_games', methods=['get'])
    def value_previous_games(self, request):
        print('value_previous_games/')
        how_many = int(request.query_params.get('how_many'))
        previous_games = int(request.query_params.get('previous_games'))
        current_game = int(request.query_params.get('current_game'))
        return Response(self._value_previous_games(how_many, previous_games, current_game),
                        status=200)
