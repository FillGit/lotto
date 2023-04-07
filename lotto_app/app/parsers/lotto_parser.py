from bs4 import BeautifulSoup


class LottoParser():

    def __init__(self, response, page, *args, **kwargs):
        self.response = response
        self.page = str(page)
        self.soup = self._get_soup()

    def plus_zero(self, number):
        if len(str(number)) == 1:
            return f'0{number}'
        return str(number)

    def _get_soup(self):
        return BeautifulSoup(self.response.text, 'lxml')

    def validate_status_code(self):
        if self.response.status_code != 200:
            raise ValueError(f'validate_status_code: {self.response.status_code}')

    def validate_game(self, game):
        if self.page != game:
            raise ValueError(f'validate_game: page={self.page}, game={game}')

    def parser_response_for_view(self):
        pass
