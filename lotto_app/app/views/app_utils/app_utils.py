from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game


class AppUtilsSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Game.objects.filter(
            name_game=self.kwargs['ng']).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())
        ).order_by('-game_id_int')

    @action(detail=False, url_path='missing_game_ids', methods=['get'])
    def missing_game_ids(self, request, ng):
        print('missing_game_ids/')
        all_game_ids = [int(_dict['game_id']) for _dict in self.get_queryset().values('game_id')]
        missing_game_ids = []
        for _id in range(all_game_ids[-1], all_game_ids[0]+1):
            if _id not in all_game_ids:
                missing_game_ids.append(_id)
        return Response(missing_game_ids, status=200)

    @action(detail=False, url_path='fist_last_game_ids', methods=['get'])
    def fist_last_game_ids(self, request, ng):
        all_game_ids = [int(_dict['game_id']) for _dict in self.get_queryset().values('game_id')]
        return Response({'first': all_game_ids[-1],
                         'last': all_game_ids[0]}, status=200)
