from rest_framework import viewsets
from lotto_app.app.serializers import GameSerializer
from lotto_app.app.models import Game
from rest_framework.decorators import action

from lotto_app.app.utils import get_game_info, index_bingo, index_9_parts
from rest_framework.response import Response


class GameModelViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_object(self):
        return Game.objects.get(game=self.kwargs['pk'])

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
            all_cost_numbers[num] = all_info[0]['cost_numbers'][snum] + \
                                    all_info[1]['cost_numbers'][snum] + \
                                    all_info[2]['cost_numbers'][snum] + \
                                    all_info[3]['cost_numbers'][snum] + \
                                    all_info[4]['cost_numbers'][snum]

        total_cost_numbers = dict((x, y) for x, y in sorted(all_cost_numbers.items(), key= lambda x: x[1]))
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
        game = request.query_params.get('game')
        game_obj = Game.objects.get(game=game)
        return Response(get_game_info(game_obj), status=200)


    @action(detail=False, url_path='five_games_info', methods=['get'])
    def five_games_info(self, request):
        print('five_games_info/')
        game = request.query_params.get('game')
        return Response(self.get_five_games_info(game), status=200)


    @action(detail=False, url_path='index_bingo_30', methods=['get'])
    def index_bingo_30(self, request):
        print('index_bingo_30/')
        game = request.query_params.get('game')
        game_obj = Game.objects.get(game=game)
        last_total_cost_numbers = self.get_five_games_info(int(game)-1)['total_cost_numbers']
        game_info = get_game_info(game_obj)
        null_numbers = {num: last_total_cost_numbers[int(num)] for num, v in game_info['cost_numbers'].items() if v==0}
        indexes = {
            'index_bingo': index_bingo(last_total_cost_numbers, game_info['bingo_30']),
            'index_9_parts': index_9_parts(last_total_cost_numbers, game_info['bingo_30']),
            'null_numbers': null_numbers,
        }
        return Response(indexes,status=200)

    @action(detail=False, url_path='value_previous_games', methods=['get'])
    def value_previous_games(self, request):
        print('value_previous_games/')
        how_many = int(request.query_params.get('how_many'))
        previous_games = int(request.query_params.get('previous_games'))
        current_game = int(request.query_params.get('current_game'))
        number_info = []
        for game in range(current_game - previous_games + 1, current_game + 1):
            print(game)
            number_info.append(get_game_info(Game.objects.get(game=int(game)))['numbers'][:how_many])

        all = {str(i): 0 for i in range(1, 91)}
        for _info in number_info:
            for num in _info:
                all[num] += 1

        return Response(all, status=200)

