from django_webtest import WebTest
from hamcrest import assert_that, calling, is_, raises
from webtest.app import AppError

from lotto_app.app.models import Game
from tests.helpers import GameFactory

numbers_1 = [61, 55, 7, 59, 63, 13, 49, 10, 48, 8, 22, 76, 39, 47, 75, 31, 23, 33, 87,
             77, 20, 44, 53, 43, 6, 18, 80, 58, 28, 62, 16, 78, 84, 21, 67, 89, 90, 36,
             79, 56, 54, 68, 46, 66, 12, 51, 72, 14, 50, 42, 17, 37, 38, 11, 64, 32, 1,
             81, 60, 70, 41, 2, 30, 74, 52, 24, 57, 40, 15, 4, 85, 5, 34, 71, 9, 82, 35,
             25, 86, 27, 73, 83, 3, 29, 88, 69, 65]

numbers_2 = [60, 89, 4, 44, 36, 57, 47, 21, 62, 51, 26, 63, 29, 66, 85, 84, 17, 23, 55,
             72, 11, 35, 67, 79, 32, 86, 5, 38, 16, 48, 33, 45, 80, 15, 88, 27, 74, 9, 49,
             46, 40, 58, 70, 14, 37, 56, 71, 77, 83, 28, 8, 81, 34, 78, 31, 43, 68, 59,
             87, 73, 64, 1, 42, 61, 25, 18, 39, 41, 20, 75, 54, 2, 10, 6, 50, 22, 12, 90,
             30, 3, 53, 24, 13, 82, 69, 52, 65]

numbers_3 = [58, 80, 72, 59, 23, 61, 70, 71, 75, 65, 82, 37, 47, 79, 2, 16, 43, 5, 60,
             54, 19, 6, 44, 49, 78, 1, 34, 11, 14, 90, 88, 36, 27, 87, 10, 69, 73, 32,
             17, 35, 55, 50, 20, 13, 8, 76, 25, 68, 45, 12, 64, 74, 51, 42, 26, 85, 28,
             52, 30, 31, 41, 7, 86, 22, 46, 39, 89, 77, 84, 66, 81, 4, 29, 15, 9, 57, 18,
             3, 21, 83, 48, 24, 53, 56, 38, 63, 33]


def get_fields_games(numbers, game_id):
    return [
        {'name_game': 'test_lotto1',
         'game_id': game_id,
         'numbers': numbers,
         'last_win_number_card': numbers[36],
         'last_win_number_ticket': numbers[61]
         }
    ]


class GamesNoNumbersTest(WebTest):
    endpoint = '/test_lotto1/research/'

    def setUp(self):
        super(GamesNoNumbersTest, self).setUp()

    def test_validate_not_enough_games(self):
        self.game_factory = GameFactory(amount_games=3)
        params = {'how_games': 1}
        assert_that(calling(self.app.get).with_args(f'{self.endpoint}3/games_no_numbers/', params=params),
                    raises(IndexError))
        assert_that(calling(self.app.get).with_args(f'{self.endpoint}4/games_no_numbers/', params=params),
                    raises(AppError))

        self.game_factory = GameFactory(amount_games=1)
        # Now we have games and get result:
        resp = self.app.get(f'{self.endpoint}4/games_no_numbers/', params=params)
        assert_that(list(resp.json.keys()), is_(['4', 'all_no_numbers_9_parts']))

    def test_happy_path_games_no_numbers(self):
        self.game_factory = GameFactory(amount_games=5)
        params = {'how_games': 2}
        resp = self.app.get(f'{self.endpoint}5/games_no_numbers/', params=params)
        assert_that(list(resp.json.keys()), is_(['5', '4', 'all_no_numbers_9_parts']))

    def test_happy_path_without_field_last_wins(self):
        GameFactory(amount_games=4, in_order_numbers=True)
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
        assert_that(Game.objects.count(), is_(6))

        params = {'how_games': 2}
        resp = self.app.get(f'{self.endpoint}6/games_no_numbers/', params=params)
        assert_that(list(resp.json.keys()), is_(['6', '4', 'all_no_numbers_9_parts']))


class ComparisonPartsWinTicketTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto1/research/{game_id}/comparison_parts_win_ticket/'

    def test_happy_path_comparison_parts_win_ticket(self):
        game_factory = [GameFactory(fields_games=get_fields_games(numbers_1, 1))]
        game_factory.append(GameFactory(amount_games=1, in_order_numbers=True))
        game_factory.append(GameFactory(fields_games=get_fields_games(numbers_2, 3)))
        game_factory.append(GameFactory(amount_games=1, in_order_numbers=True))
        game_factory.append(GameFactory(fields_games=get_fields_games(numbers_3, 5)))
        params = {'how_comparison_games': 4,
                  'part_consists_of': 5,
                  'order_row': 8,
                  }

        resp = self.app.get(self._get_endpoint(5), params=params)

        assert_that(list(resp.json.keys()), is_(['main_game', '4', '3', '2', '1']))
        assert_that(resp.json['main_game'], is_('5'))
        assert_that(resp.json['2'], is_([]))
        assert_that(resp.json['4'], is_([]))
        assert_that(resp.json['3'], is_([]))
        assert_that(resp.json['1'], is_([[6, 7, 8, 10, 11], [7, 8, 10, 11, 12],
                                         [8, 10, 11, 12, 13], [10, 11, 12, 13, 14],
                                         [11, 12, 13, 14, 16], [12, 13, 14, 16, 17]]))


class Games9PartsIntoWinTicketTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto1/research/{game_id}/games_9_parts_into_win_ticket/'

    def test_happy_path_games_9_parts_into_win_ticket(self):
        game_factory = [GameFactory(fields_games=get_fields_games(numbers_1, 1))]
        game_factory.append(GameFactory(amount_games=1, in_order_numbers=True))
        game_factory.append(GameFactory(fields_games=get_fields_games(numbers_2, 3)))
        game_factory.append(GameFactory(amount_games=1, in_order_numbers=True))
        game_factory.append(GameFactory(fields_games=get_fields_games(numbers_3, 5)))
        params = {'how_games': 2}

        resp = self.app.get(self._get_endpoint(5), params=params)

        assert_that(list(resp.json.keys()), is_(['5', '4', 'all_games_index_9_parts']))
        assert_that(resp.json['all_games_index_9_parts'],
                    is_({'0': 20, '1': 24, '2': 24, '3': 26, '4': 28, '5': 28, '6': 30, '8': 32,
                         '7': 32}))
        assert_that(resp.json['4'], is_({'0': 2, '1': 5, '2': 4, '3': 7, '4': 9, '5': 7, '6': 8,
                                         '7': 8, '8': 10}))
        assert_that(sum(resp.json['4'].values()), is_(60))
        assert_that(resp.json['5'], is_({'0': 8, '1': 7, '2': 8, '3': 6, '4': 5, '5': 7, '6': 7,
                                         '7': 8, '8': 6}))
        assert_that(sum(resp.json['5'].values()), is_(62))
