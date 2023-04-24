import re

from lotto_app.app.models import Game
from lotto_app.app.parsers.lotto_parser import LottoParser


class Parser90Numbers(LottoParser):

    def _get_calc_no_numbers(self, str_numbers):
        _str_all_numbers = sorted([self.plus_zero(num) for num in range(1, 91)])
        list_str_no_numbers = [num for num in _str_all_numbers
                               if num not in Game.get_list_str_numbers(str_numbers)]
        if list_str_no_numbers:
            return ''.join(list_str_no_numbers)
        return None

    def _validate_no_number(self, str_no_numbers, str_numbers):
        calc_str_no_numbers = self._get_calc_no_numbers(str_numbers)
        if str_no_numbers != calc_str_no_numbers:
            raise ValueError(
                f'_validate_no_number: no_numbers={str_no_numbers}, calculated_no_numbers={calc_str_no_numbers}')

    def _validate_numbers(self, value):
        list_str_numbers = Game.get_list_str_numbers(value, True)
        not_numeric = [n for n in list_str_numbers if n.isnumeric() is False]
        if not_numeric:
            raise ValueError(
                f"You don't have a numerical value - {not_numeric}")
        many_symbols = [n for n in list_str_numbers if len(n) > 2]
        if many_symbols:
            raise ValueError(
                f"There is a value that has more than 2 characters - {many_symbols}")

    def parser_response_for_view(self):
        self.validate_status_code()

        number_tags = self.soup.find_all('td', {'class': 'word-wrap'})
        dirty_numbers = [tag.text.replace('\n', '') for tag in number_tags][0::2]
        str_numbers = ''.join([_num for _num in dirty_numbers if _num.isnumeric()])
        self._validate_numbers(str_numbers)

        game_tags = self.soup.find('div', id='content').find('h1')
        game_id = re.search(r'№\d{3,4},', game_tags.text)[0].replace('№', '').replace(',', '')
        self.validate_game(game_id)

        if (len(str_numbers) != 180):
            no_number_tags = self.soup.find('div', class_='drawing_win_numbers barrels').find_all('li')
            str_no_numbers = ''.join([tag.text for tag in no_number_tags])
            self._validate_no_number(str_no_numbers, str_numbers)

        return {'str_numbers': str_numbers,
                'last_win_number_card': dirty_numbers[1][-2:],
                'last_win_number_ticket': dirty_numbers[2][-2:],
                'game_id': game_id,
                'name_game': self.name_game,
                }
