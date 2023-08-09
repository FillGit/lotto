import re

from lotto_app.app.parsers.lotto_parser import LottoParser


class Parser8AddNumbers(LottoParser):

    def _validate_x_texts(self, _x_texts):
        not_numeric = [n for n in _x_texts if n.isnumeric() is False]
        if not_numeric:
            raise ValueError(
                f"You don't have a numerical value - {not_numeric}")
        many_symbols = [n for n in _x_texts if len(n) > 2]
        if many_symbols:
            raise ValueError(
                f"There is a value that has more than 2 characters - {many_symbols}")
        if len(_x_texts) != 9:
            raise ValueError(
                f"We should have 9 numbers, but we have {len(_x_texts)} numbers.")

    def _validate_add_numbers(self, add_numbers):
        _x_text = self.soup.find('div', {'class': 'winning_numbers cleared'}).find('li', {'class': 'extra'}).text
        if add_numbers != [int(_x_text)]:
            raise ValueError("add_numbers is not correct")

    def parser_response_for_view(self):
        self.validate_status_code()

        _x_texts = [tag.text for tag in self.soup.find('div', {'class': 'winning_numbers cleared'}).find_all('p')]
        self._validate_x_texts(_x_texts)
        numbers = [int(_t) for _t in _x_texts[0:8]]
        add_numbers = [int(_x_texts[8])]
        self._validate_add_numbers(add_numbers)

        game_tags = self.soup.find('div', id='content').find('h1')
        game_id = re.search(r'№ \d{6,7},', game_tags.text)[0].replace('№ ', '').replace(',', '')
        self.validate_game(game_id)

        return {'numbers': numbers,
                'add_numbers': add_numbers,
                'game_id': game_id,
                'name_game': self.name_game,
                }
