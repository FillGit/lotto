from rest_framework import viewsets
from lotto_app.app.serializers import GameSerializer
from lotto_app.app.models import Game


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer