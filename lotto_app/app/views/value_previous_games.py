from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.response import Response

from lotto_app.app.models import Game


class ValuePreviousGamesViewSet(viewsets.ModelViewSet):

    @staticmethod
    def value_previous_games(name_game, how_numbers, previous_games, current_game):
        value_previous_games = {i: 0 for i in range(1, 91)}
        number_info = []

        game_objs = Game.objects.filter(
            name_game=name_game,
            last_win_number_card__isnull=False,
            last_win_number_ticket__isnull=False
        ).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        ).filter(game_id_int__lte=current_game, game_id_int__gte=current_game-previous_games-5
                 ).order_by('-game_id_int')

        for game_obj in game_objs[0:previous_games]:
            if not how_numbers:
                how_numbers = game_obj.get_win_ticket()['by_account']
            number_info.append(game_obj.numbers[:int(how_numbers)])

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
