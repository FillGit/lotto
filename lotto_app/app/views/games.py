from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game
from lotto_app.app.parsers.choise_parsers import ChoiseParsers
from lotto_app.app.serializers import GameSerializer
from lotto_app.app.utils import get_game_info, index_9_parts, index_bingo
from lotto_app.app.views.value_previous_games import ValuePreviousGamesViewSet
from lotto_app.config import get_amount_games, get_factor_games


class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer

    def get_queryset(self):
        return Game.objects.filter(
            name_game=self.kwargs['ng']).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        ).order_by('-game_id_int')

    def get_object(self):
        return Game.objects.get(name_game=self.kwargs['ng'], game_id=self.kwargs['pk'])

    def game_request(self):
        game_id = int(self.kwargs['pk'])
        return game_id, Game.objects.get(name_game=self.kwargs['ng'], game_id=game_id)

    @staticmethod
    def get_several_games_info(ng, game_id):
        all_cost_numbers = {}
        amount_games = get_amount_games()
        factor_games = get_factor_games(amount_games)

        q_games = Game.objects.filter(
            name_game=ng,
            last_win_number_card__isnull=False,
            last_win_number_ticket__isnull=False
        ).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        ).filter(game_id_int__lte=game_id, game_id_int__gte=game_id-amount_games-5
                 ).order_by('-game_id_int')
        all_info = [get_game_info(q_games[i], float(factor_games[i])) for i in range(0, amount_games)]

        for num in range(1, 91):
            all_cost_numbers[num] = sum(
                [all_info[i]['cost_numbers'][num] for i in range(0, amount_games)])

        total_cost_numbers = dict((x, y) for x, y in sorted(all_cost_numbers.items(),
                                                            key=lambda x: x[1]))
        str_total_cost_numbers = [{k: y} for k, y in total_cost_numbers.items()]
        return {
            'min_cost': str_total_cost_numbers[0],
            'max_cost': str_total_cost_numbers[89],
            'total_cost_numbers': total_cost_numbers,
        }

    @staticmethod
    def get_several_games_no_numbers(total_cost_numbers, game_info):
        return {num: total_cost_numbers[int(num)] for num, v in game_info['cost_numbers'].items() if
                v == 0}

    @action(detail=True, url_path='info', methods=['get'])
    def info(self, request, ng, pk):
        print('info/')
        game_id, game_obj = self.game_request()
        factor_games = get_factor_games(1)
        return Response(get_game_info(game_obj, factor_games[0]), status=200)

    @action(detail=True, url_path='several_games_info', methods=['get'])
    def several_games_info(self, request, ng, pk):
        print('several_games_info/')
        game_id, game_obj = self.game_request()
        return Response(self.get_several_games_info(ng, game_id), status=200)

    def _condition_numbers(self, previous_games, current_game, condition):
        _value_previous_games = ValuePreviousGamesViewSet.value_previous_games(
            self.kwargs['ng'], None, previous_games, current_game)
        print(previous_games, current_game, _value_previous_games)

        return {int(num) for num, value in _value_previous_games.items() if value == condition}

    def _get_good_numbers(self, game_id, good_games):
        return self._condition_numbers(good_games, game_id, 0)

    def _get_bad_numbers(self, game_id, bad_games):
        bad_numbers = set()
        for i in range(1, bad_games+1):
            bad_numbers.update(self._condition_numbers(bad_games, game_id, bad_games))
        return bad_numbers

    @action(detail=True, url_path='future_game_30', methods=['get'])
    def future_game_30(self, request, ng, pk):
        print('future_game_30/')
        good_games = int(request.query_params.get('good_games'))
        bad_games = int(request.query_params.get('bad_games'))
        game_id, game_obj = self.game_request()
        total_cost_numbers = self.get_several_games_info(ng, game_id)['total_cost_numbers']
        game_info = get_game_info(game_obj)

        indexes = {
            'index_bingo': index_bingo(total_cost_numbers, game_info['bingo_30']),
            'index_9_parts': index_9_parts(total_cost_numbers, game_info['bingo_30']),
            'good_numbers': self._get_good_numbers(game_id, good_games),
            'bad_numbers': self._get_bad_numbers(game_id, bad_games),
        }
        return Response(indexes, status=200)

    @action(detail=False, url_path='parsers', methods=['post'])
    def parsers(self, request, ng):
        print('parsers/')
        name_game = ng
        page = request.data['page']
        class_parser = ChoiseParsers(name_game, page).get_class_parser()
        serializer = self.get_serializer(data=class_parser.parser_response_for_view())
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=False, url_path='parsers_mult_pages', methods=['post'])
    def parsers_mult_pages(self, request, ng):
        print('parsers_mult_pages/')
        name_game = ng
        page_start = request.data['page_start']
        page_end = request.data['page_end']
        list_serializers = []
        for page in range(page_start, page_end+1):
            class_parser = ChoiseParsers(name_game, page).get_class_parser()
            serializer = self.get_serializer(data=class_parser.parser_response_for_view())
            serializer.is_valid(raise_exception=True)
            list_serializers.append(serializer)

        serializer_dataset = []
        for serializer in list_serializers:
            self.perform_create(serializer)
            serializer_dataset.append(serializer.data)

        return Response(serializer_dataset, status=201)
