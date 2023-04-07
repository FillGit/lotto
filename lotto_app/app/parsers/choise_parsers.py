import requests

from lotto_app.config import get_class_parser, get_from_config, get_section_from_config


class ChoiseParsers():
    LOTTO_HEADERS = get_section_from_config('lotto_headers')

    def __init__(self, name_game, page, *args, **kwargs):
        self.name_game = name_game
        self.page = page

    def get_class_parser(self):
        _url_archive = get_from_config('lotto_url', f'url_archive_{self.name_game}')
        _url_archive_page = f'{_url_archive}{self.page}'
        response = requests.get(f'{_url_archive_page}', self.LOTTO_HEADERS)
        return get_class_parser(self.name_game)(response, self.page)
