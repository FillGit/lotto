from lotto_app.app.models import Game
from lotto_app.app.utils import record_correction_game_numbers


def fix_record_all_game_numbers():
    game_objs = Game.objects.all()
    for game_obj in game_objs:
        game_obj.numbers = " ".join(record_correction_game_numbers(game_obj.numbers))
        game_obj.save(update_fields=['numbers'])
