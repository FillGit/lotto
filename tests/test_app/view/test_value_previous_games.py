from django_webtest import WebTest
from hamcrest import assert_that, calling, has_length, is_, is_not, raises

from lotto_app.app.models import Game
from tests.helpers import GameFactory90


class ValuePreviousGamesTest(WebTest):
    endpoint = '/test_lotto1/value_previous_games/'

    def setUp(self):
        super(ValuePreviousGamesTest, self).setUp()

    def test_happy_path_value_previous_games(self):
        self.game_factory = GameFactory90(amount_games=5, in_order_numbers=True)
        params = {'how_numbers': 45,
                  'previous_games': 5,
                  }
        resp = self.app.get(f'{self.endpoint}5/', params=params)
        assert_that(resp.json, has_length(90))
        expected_result = {str(i): 5 for i in range(1, 46)}
        expected_result.update({str(i): 0 for i in range(46, 91)})
        assert_that(resp.json, is_(expected_result))

    def test_happy_path_without_how_numbers(self):
        self.game_factory = GameFactory90(amount_games=5)
        params = {'previous_games': 3}
        resp = self.app.get(f'{self.endpoint}5/', params=params)
        expected_result = {str(i): 3 for i in range(1, 61)}
        expected_result.update({str(i): 0 for i in range(61, 91)})
        assert_that(resp.json, has_length(90))
        assert_that(resp.json.keys(), is_(expected_result.keys()))
        assert_that(resp.json, is_not(expected_result))

    def test_validate_not_params(self):
        self.game_factory = GameFactory90(amount_games=5)
        assert_that(calling(self.app.get).with_args(f'{self.endpoint}5/', params={}),
                    raises(TypeError))

    def test_happy_path_without_field_last_wins_in_one_game(self):
        self.game_factory = GameFactory90(amount_games=3)
        _fields_games = GameFactory90(amount_games=1,
                                      only_games_json=True).get_game_json()
        GameFactory90(fields_games=[{
            'name_game': _fields_games['name_game'],
            'game_id': _fields_games['game_id'],
            'numbers': _fields_games['numbers'],
            'no_numbers': _fields_games['no_numbers']
        }])
        GameFactory90(amount_games=1)

        assert_that(Game.objects.count(), is_(5))

        params = {'previous_games': 3}
        resp = self.app.get(f'{self.endpoint}5/', params=params)
        expected_result = {str(i): 3 for i in range(1, 61)}
        expected_result.update({str(i): 0 for i in range(61, 91)})
        assert_that(resp.json, has_length(90))
        assert_that(resp.json.keys(), is_(expected_result.keys()))
        assert_that(resp.json, is_not(expected_result))
