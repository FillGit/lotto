from bs4 import BeautifulSoup


class LottoParser():

    def __init__(self, response, *args, **kwargs):
        self.response = response
        self.soup = self._get_soup

    def _get_soup(self):
        return BeautifulSoup(self.response.text, 'lxml')

    def parser_response_for_view(self):
        pass
