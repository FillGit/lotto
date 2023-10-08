import datetime

import pytz

from lotto_app.app.parsers.lotto_parser import LottoParser


class ParserCommand8Add(LottoParser):

    def validate_game_id(self, game_id):
        if not game_id.isnumeric():
            raise ValueError(
                f"You don't have a numerical value - {game_id}")

        if len(game_id) != 6:
            raise ValueError(
                f"We should have 6 numbers, but we have {len(game_id)} numbers.")

    def parser_response_for_view(self):
        self.validate_status_code()
        _x_texts = [tag.text for tag in self.soup.find('div', {'class': 'main'})]
        _time_obj = datetime.datetime.strptime(_x_texts[1].replace('\n', ''), '%d.%m.%Y %H:%M:%S')
        time_em = pytz.timezone('Europe/Moscow').localize(_time_obj)

        game_id = _x_texts[2].replace('\n', '')
        self.validate_game_id(game_id)
        return {'game_id': game_id, 'time_obj': _time_obj, 'time_em': time_em, 'draft_data': _x_texts[3]}
