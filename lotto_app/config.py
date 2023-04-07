from django.conf import settings

from lotto_app.constants import LOTTO_PARSER


def get_section_from_config(section, default=None):
    default = default or {}
    try:
        result = dict(settings.CONFIG.items(section)) if settings.CONFIG.has_section(section) else default
    except Exception as e:
        raise e.__class__(f"Error while trying to read section: {section} -- {str(e)}")
    return result


def get_from_config(section, option, default=None):
    if isinstance(default, dict):
        default = default.get(option)
    section_opts = get_section_from_config(section)
    return section_opts.get(option, default)


def get_amount_games():
    return int(get_from_config('amount_games', 'amount'))


def get_factor_games(amount_games=5):
    return [float(get_from_config('factor_games', f'game-{factor}')) for factor in range(1, amount_games+1)]


def get_class_parser(name_game):
    return LOTTO_PARSER[get_from_config('lotto_parsers', f'parser_{name_game}')]
