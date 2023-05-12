from lotto_app.app.models import LottoTickets
from lotto_app.app.views.games import GameViewSet


def get_set_numbers(name_game, game_id, list_parts, add_numbers):
    several_games_info = GameViewSet.get_several_games_info(name_game, game_id)
    list_numbers = []
    for i in list_parts:
        list_numbers.extend(several_games_info['9_parts_numbers'][i])
    return set(list_numbers + add_numbers)


def easy_pc_choice(name_game, game_id, set_numbers):
    lt_objs = LottoTickets.objects.filter(name_game=name_game, game_id=game_id)
    tickets = {}
    for obj in lt_objs:
        print(obj, set(obj.ticket_numbers))
        if len(set(obj.ticket_numbers) & set_numbers) >= 25:
            tickets[obj.ticket_id] = obj.first_seven_numbers
    return tickets
