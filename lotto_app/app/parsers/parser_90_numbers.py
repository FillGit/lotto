from lotto_app.app.parsers.lotto_parser import LottoParser


class Parser90numbers(LottoParser):

    def parser_response_for_view(self):
        print(self.response.status_code)
        return {'Parser90numbers': 'Ok'}
