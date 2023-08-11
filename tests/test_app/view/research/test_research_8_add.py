from django_webtest import WebTest
from hamcrest import assert_that, contains_inanyorder, is_

from tests.helpers import Fake8Numbers as F8Ns
from tests.helpers import GameFactory8AddNumbers as GF8As


def get_fields_games(numbers, add_numbers, game_id):
    return [
        {'name_game': 'test_lotto2',
         'game_id': game_id,
         'numbers': numbers,
         'add_numbers': add_numbers
         }
    ]


def get_standart_game_obj():
    GF8As(fields_games=get_fields_games(F8Ns.numbers_1, [1], 1))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_2, [2], 2))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_3, [3], 3))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_4, [4], 4))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_5, [4], 5))


class ComparisonAllNumbersTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/comparison_all_numbers/'

    def test_happy_path_comparison_all_numbers(self):
        get_standart_game_obj()

        resp = self.app.get(self._get_endpoint(5))
        assert_that(resp.json.keys(),
                    contains_inanyorder('main_game', '1', '3', '2', '4'))
        assert_that(resp.json['main_game'], is_('5'))
        assert_that(resp.json['1'], is_([4, [2, 3, 5, 20]]))
        assert_that(resp.json['2'], is_([3, [4, 12, 13]]))
        assert_that(resp.json['3'], is_([3, [2, 5, 17]]))
        assert_that(resp.json['4'], is_([4, [2, 3, 13, 20]]))


class CombinationOptionsTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/combination_options/'

    def test_happy_path_combination_options(self):
        get_standart_game_obj()
        params = {'how_games': 2}

        resp = self.app.get(self._get_endpoint(5), params=params)

        assert_that(list(resp.json.keys()),
                    is_(['5', '4', '4, 2, 1, 1', '2, 1, 1, 1, 1, 1, 1']))
        assert_that(resp.json['5'], is_([4, 2, 1, 1]))
        assert_that(resp.json['4'], is_([2, 1, 1, 1, 1, 1, 1]))
        assert_that(resp.json['4, 2, 1, 1'], is_(1))
        assert_that(resp.json['2, 1, 1, 1, 1, 1, 1'], is_(1))
