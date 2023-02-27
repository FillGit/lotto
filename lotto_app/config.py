from django.conf import settings


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


def get_factor_games():
    return [float(get_from_config('factor_games', f'game-{factor}')) for factor in range(1, 6)]
