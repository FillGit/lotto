from rest_framework import status, viewsets
from rest_framework.response import Response

from lotto_app.app.models import Game, StateNumbers
from lotto_app.app.serializers import StateNumberSerializer


class StateNumbersViewSet(viewsets.ModelViewSet):
    queryset = StateNumbers.objects.all()
    serializer_class = StateNumberSerializer

    def get_state_number_objs(self):
        return StateNumbers.objects.filter(game_obj__game=self.kwargs['pk'])

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_state_number_objs(), many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.get_state_number_objs().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        game_obj = Game.objects.get(game=request.data['game'])
        state_numbers = []
        for i in range(1, 91):
            state_numbers.append(StateNumbers(game_obj=game_obj, number=i, state='low'))
        try:
            StateNumbers.objects.bulk_create(state_numbers)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        return Response([], status=status.HTTP_201_CREATED)
