import requests

from lotto_app.config import get_class_parser, get_from_config, get_section_from_config


class ChoiseParsers():
    LOTTO_HEADERS = get_section_from_config('lotto_headers')

    def __init__(self, name_game, *args, **kwargs):
        self.name_game = name_game
        if 'page' in kwargs:
            self.page = kwargs['page']

    def get_class_parser(self):
        lotto_url_archive = get_from_config('lotto_url', f'url_archive_{self.name_game}')
        response = requests.get(lotto_url_archive, self.LOTTO_HEADERS)
        return get_class_parser(self.name_game)(response)
