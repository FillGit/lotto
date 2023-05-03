from django_webtest import WebTest
from hamcrest import assert_that, calling, is_, raises
from webtest.app import AppError

from lotto_app.app.models import Game
from tests.helpers import GameFactory


class GamesNoNumbersTest(WebTest):
    endpoint = '/test_lotto1/research/'

    def setUp(self):
        super(GamesNoNumbersTest, self).setUp()

    def test_validate_not_enough_games(self):
        self.game_factory = GameFactory(amount_games=2)
        params = {'how_games': 1}
        assert_that(calling(self.app.get).with_args(f'{self.endpoint}2/games_no_numbers/', params=params),
                    raises(IndexError))
        assert_that(calling(self.app.get).with_args(f'{self.endpoint}3/games_no_numbers/', params=params),
                    raises(AppError))

        self.game_factory = GameFactory(amount_games=1)
        # Now we have games and get result:
        resp = self.app.get(f'{self.endpoint}3/games_no_numbers/', params=params)
        assert_that(list(resp.json.keys()), is_(['3', 'all_no_numbers_9_parts']))

    def test_happy_path_games_no_numbers(self):
        self.game_factory = GameFactory(amount_games=5)
        params = {'how_games': 3}
        resp = self.app.get(f'{self.endpoint}5/games_no_numbers/', params=params)
        assert_that(list(resp.json.keys()), is_(['5', '4', '3', 'all_no_numbers_9_parts']))

    def test_happy_path_without_field_last_wins(self):
        GameFactory(amount_games=3, in_order_numbers=True)
        _fields_games = GameFactory(amount_games=1,
                                    no_numbers_in_lotto=2,
                                    only_games_json=True).get_game_json()
        GameFactory(amount_games=1,
                    fields_games=[{
                        'name_game': _fields_games['name_game'],
                        'game_id': _fields_games['game_id'],
                        'numbers': _fields_games['numbers'],
                        'no_numbers': _fields_games['no_numbers']
                    }])
        GameFactory(amount_games=1, in_order_numbers=True)
        assert_that(Game.objects.count(), is_(5))

        params = {'how_games': 2}
        resp = self.app.get(f'{self.endpoint}5/games_no_numbers/', params=params)
        assert_that(list(resp.json.keys()), is_(['5', '3', 'all_no_numbers_9_parts']))
