from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework import viewsets

from lotto_app.app.models import Game


class ResearchViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Game.objects.filter(name_game=self.kwargs['ng']).order_by('game_id')

    def get_game_obj(self):
        return Game.objects.get(game_id=self.kwargs['pk'], name_game=self.kwargs['ng'])

    def get_general_game_objs(self):
        name_game = self.kwargs['ng']
        return Game.objects.filter(
            name_game=name_game,
            last_win_number_card__isnull=False,
            last_win_number_ticket__isnull=False
        ).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        )
