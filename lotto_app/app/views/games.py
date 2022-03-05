from rest_framework import viewsets
from lotto_app.app.serializers import GameSerializer
from lotto_app.app.models import Game


class GameModelViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_object(self):
        return Game.objects.get(game=self.kwargs['pk'])
