from rest_framework import viewsets
from rest_framework.response import Response

from lotto_app.app.models import Game
from lotto_app.app.utils import get_game_info


class ValuePreviousGamesViewSet(viewsets.ModelViewSet):

    @staticmethod
    def value_previous_games(name_game, how_numbers, previous_games, current_game):
        value_previous_games = {i: 0 for i in range(1, 91)}
        number_info = []

        game_objs = Game.objects.filter(
            name_game=name_game,
            game_id__in=[g for g in range(current_game - previous_games + 1, current_game + 1)])
        for game_obj in game_objs:
            if not how_numbers:
                how_numbers = game_obj.get_win_ticket()['by_account']
            number_info.append(get_game_info(game_obj)['numbers'][:int(how_numbers)])

        for _info in number_info:
            for num in _info:
                value_previous_games[num] += 1
        return value_previous_games

    def retrieve(self, request, *args, **kwargs):
        name_game = self.kwargs['ng']
        how_numbers = request.query_params.get('how_numbers', None)
        previous_games = int(request.query_params.get('previous_games'))
        current_game = int(self.kwargs['pk'])
        return Response(self.value_previous_games(name_game, how_numbers, previous_games, current_game),
                        status=200)
