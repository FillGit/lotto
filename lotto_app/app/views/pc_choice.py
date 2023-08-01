from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lotto_app.app.models import LottoTickets


class PcChoiceViewSet(ViewSet):

    def _other_numbers(self, set_numbers, ticket_numbers):
        return set(ticket_numbers) - set_numbers

    def _pc_choice_from_set_numbers(self,
                                    lt_objs,
                                    set_numbers,
                                    limit,
                                    exclude_numbers):
        tickets = {}
        for obj in lt_objs:
            len_from_set_numbers = len(set(obj.ticket_numbers) & set_numbers)
            if len_from_set_numbers >= limit and not set(exclude_numbers) & set(obj.ticket_numbers):
                tickets[obj.ticket_id] = [
                    obj.first_seven_numbers,
                    {
                     'len_from_set_numbers': len_from_set_numbers,
                     f'30-len_from_set_numbers ({30-len_from_set_numbers})': self._other_numbers(
                         set_numbers, obj.ticket_numbers),
                     },
                ]
        return tickets

    def _pc_choice_from_future_combination_win_ticket(self,
                                                      lt_objs,
                                                      set_numbers,
                                                      limit,
                                                      exclude_numbers,
                                                      future_combination_win_ticket):
        set_fcwt = set(future_combination_win_ticket)
        tickets = {}
        for obj in lt_objs:
            len_from_set_fcwt = len(set(obj.ticket_numbers) & set_fcwt)
            len_from_set_numbers = len(set(obj.ticket_numbers) & set_numbers)
            if len_from_set_fcwt >= limit and not set(exclude_numbers) & set(obj.ticket_numbers):
                tickets[obj.ticket_id] = [
                    obj.first_seven_numbers,
                    {'len_from_set_fcwt': len_from_set_fcwt,
                     'len_from_set_numbers ': len_from_set_numbers,
                     f'30-len_from_set_numbers ({30-len_from_set_numbers})': self._other_numbers(
                         set_numbers, obj.ticket_numbers),
                     },
                ]
        return tickets

    def _easy_30_pc_choice(self, name_game, game_id, set_numbers, limit, exclude_numbers,
                           future_combination_win_ticket=None):
        lt_objs = LottoTickets.objects.filter(name_game=name_game, game_id=game_id)
        if future_combination_win_ticket:
            return self._pc_choice_from_future_combination_win_ticket(lt_objs,
                                                                      set_numbers,
                                                                      limit,
                                                                      exclude_numbers,
                                                                      future_combination_win_ticket)
        return self._pc_choice_from_set_numbers(lt_objs,
                                                set_numbers,
                                                limit,
                                                exclude_numbers,
                                                )

    @action(detail=True, url_path='choice_30', methods=['post'])
    def choice_30(self, request, ng, pk=None):
        name_game = self.kwargs['ng']
        game_id = self.kwargs['pk']
        set_numbers = set(request.data['set_numbers'])
        limit = request.data['limit']
        exclude_numbers = request.data.get('exclude_numbers', [])
        future_combination_win_ticket = request.data.get('future_combination_win_ticket', None)
        return Response(
            self._easy_30_pc_choice(name_game,
                                    game_id,
                                    set_numbers,
                                    limit,
                                    exclude_numbers,
                                    future_combination_win_ticket),
            status=200)
