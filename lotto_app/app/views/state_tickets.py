from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import LottoTickets, StateNumbers
from lotto_app.app.serializers import StateNumberSerializer


class StateNumbersViewSet(viewsets.ModelViewSet):
    queryset = StateNumbers.objects.all()
    serializer_class = StateNumberSerializer

    def get_state_number_objs(self):
        return StateNumbers.objects.filter(name_game=self.kwargs['ng'],
                                           game_id=self.kwargs['pk'])

    def lotto_tickets_by_game_objs(self, game_id=None):
        name_game = self.kwargs['ng']
        if not game_id:
            game_id = self.kwargs['pk']
        return LottoTickets.objects.filter(name_game=name_game, game_id=game_id)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_state_number_objs().order_by('number'), many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.get_state_number_objs().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        state_numbers = []
        for i in range(1, 91):
            state_numbers.append(StateNumbers(name_game=self.kwargs['ng'],
                                              game_id=request.data['game_id'],
                                              number=i
                                              ))
        try:
            sn = StateNumbers.objects.bulk_create(state_numbers)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(sn, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path='ticket_used', methods=['post'])
    def ticket_used(self, request, ng, pk):
        ticket_obj = self.lotto_tickets_by_game_objs().get(ticket_id=request.data['ticket_id'],
                                                           taken_ticket=False)
        sn_objs = self.get_state_number_objs()
        for obj in sn_objs:
            if obj.number in ticket_obj.ticket_numbers:
                obj.amount_used += 1

        StateNumbers.objects.bulk_update(sn_objs, ['amount_used'])
        ticket_obj.taken_ticket = True
        ticket_obj.save()

        serializer = self.get_serializer(sn_objs.order_by('number'), many=True)
        return Response(serializer.data)
