from lotto_app.app.models import Game


def fix_name_game_study():
    study_objs = [obj for obj in Game.objects.all() if int(obj.game_id) < 700]
    for game_obj in study_objs:
        game_obj.name_game = "study"
        game_obj.save(update_fields=['name_game'])
