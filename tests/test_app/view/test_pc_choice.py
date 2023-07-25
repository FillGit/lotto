from django_webtest import WebTest
from hamcrest import assert_that, is_

from tests.helpers import Fake30Numbers as F30Ns
from tests.helpers import Ticket30Factory


def get_fields_ticket(ticket_numbers, game_id, ticket_id):
    return [
        {'name_game': 'test_lotto1',
         'game_id': game_id,
         'ticket_id': ticket_id,
         'ticket_numbers': ticket_numbers,
         'first_seven_numbers': ticket_numbers[0:7]
         }
    ]


class Choice30Test(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto1/pc_choice/{game_id}/choice_30/'

    def test_happy_path_choice_30(self):
        Ticket30Factory(fields_tickets=get_fields_ticket(F30Ns.numbers_1, 1, 1))
        Ticket30Factory(fields_tickets=get_fields_ticket(F30Ns.numbers_2, 1, 2))
        Ticket30Factory(fields_tickets=get_fields_ticket(F30Ns.numbers_3, 1, 3))
        Ticket30Factory(fields_tickets=get_fields_ticket(F30Ns.numbers_4, 1, 4))
        Ticket30Factory(fields_tickets=get_fields_ticket(F30Ns.numbers_5, 1, 5))

        # without "future_combination_win_ticket"
        params = {"set_numbers": [1, 2, 3, 4, 5, 6, 7, 8],
                  "limit": 4,
                  "exclude_numbers": [],
                  "future_combination_win_ticket": []
                  }
        resp = self.app.post_json(self._get_endpoint(1), params=params)
        assert_that(resp.json,
                    is_({'5': [[64, 19, 57, 84, 2, 48, 11],
                               {'len_from_set_numbers': 4,
                                '30-len_from_set_numbers (26)': [11, 12, 19, 20, 26, 27, 28, 35, 37,
                                                                 38, 40, 41, 47, 48, 51, 57, 62, 63,
                                                                 64, 66, 71, 76, 77, 84, 85, 86]}
                               ]}))

        # with "future_combination_win_ticket"
        params = {"set_numbers": [1, 2, 3, 4, 5, 6, 7, 8],
                  "limit": 4,
                  "exclude_numbers": [],
                  "future_combination_win_ticket": [1, 2, 3, 4, 5, 6, 7, 8, 11]
                  }
        resp = self.app.post_json(self._get_endpoint(1), params=params)
        assert_that(resp.json,
                    is_({'5': [[64, 19, 57, 84, 2, 48, 11],
                               {'len_from_set_fcwt': 5,
                                'len_from_set_numbers ': 4,
                                '30-len_from_set_numbers (26)': [11, 12, 19, 20, 26, 27, 28, 35,
                                                                 37, 38, 40, 41, 47, 48, 51, 57,
                                                                 62, 63, 64, 66, 71, 76, 77, 84,
                                                                 85, 86]}]}))
