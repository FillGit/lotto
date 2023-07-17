from django_webtest import WebTest
from hamcrest import assert_that, calling, is_, is_not, raises
from webtest.app import AppError

from lotto_app.app.models import Game
from tests.helpers import FakeNumbers as FNs
from tests.helpers import GameFactory


def get_fields_games(numbers, game_id):
    return [
        {'name_game': 'test_lotto1',
         'game_id': game_id,
         'numbers': numbers,
         'last_win_number_card': numbers[36],
         'last_win_number_ticket': numbers[61]
         }
    ]


class ResearchTest(WebTest):
    def get_endpoint(self, game_id, url_name):
        return f'/test_lotto1/research/{game_id}/{url_name}/'


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
        game_factory = [GameFactory(fields_games=get_fields_games(FNs.numbers_1, 1))]
        game_factory.append(GameFactory(amount_games=1, in_order_numbers=True))
        game_factory.append(GameFactory(fields_games=get_fields_games(FNs.numbers_2, 3)))
        game_factory.append(GameFactory(amount_games=1, in_order_numbers=True))
        game_factory.append(GameFactory(fields_games=get_fields_games(FNs.numbers_3, 5)))
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

    def test_comparison_parts_win_ticket(self):
        [GameFactory(fields_games=get_fields_games(FNs.numbers_3, 1)),
         GameFactory(fields_games=get_fields_games(FNs.numbers_2, 2)),
         GameFactory(fields_games=get_fields_games(FNs.numbers_1, 3))]
        params = {'how_comparison_games': 4,
                  'part_consists_of': 5,
                  'order_row': 8,
                  }

        resp = self.app.get(self._get_endpoint(3), params=params)

        assert_that(list(resp.json.keys()), is_(['main_game', '2', '1']))
        assert_that(resp.json['main_game'], is_('3'))
        assert_that(resp.json['2'], is_([[62, 63, 64, 66, 67], [63, 64, 66, 67, 68], [64, 66, 67, 68, 70],
                                         [77, 78, 79, 80, 81]]))
        assert_that(resp.json['1'], is_([[6, 7, 8, 10, 11], [7, 8, 10, 11, 12],
                                         [8, 10, 11, 12, 13], [10, 11, 12, 13, 14],
                                         [11, 12, 13, 14, 16], [12, 13, 14, 16, 17]]))


class Games9PartsIntoWinTicketTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto1/research/{game_id}/games_9_parts_into_win_ticket/'

    def test_happy_path_games_9_parts_into_win_ticket(self):
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 1))
        GameFactory(amount_games=1, in_order_numbers=True)
        GameFactory(fields_games=get_fields_games(FNs.numbers_2, 3))
        GameFactory(amount_games=1, in_order_numbers=True)
        GameFactory(fields_games=get_fields_games(FNs.numbers_3, 5))

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


class FutureCombinationWinTicketTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto1/research/{game_id}/future_combination_win_ticket/'

    def test_happy_path_future_combination_win_ticket(self):
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 1))
        GameFactory(amount_games=1, in_order_numbers=True)
        GameFactory(fields_games=get_fields_games(FNs.numbers_3, 3))
        GameFactory(amount_games=1, in_order_numbers=True)

        params = {'parts_by_used': '2,3,6,8',
                  'add_numbers': '12,14'}

        resp = self.app.get(self._get_endpoint(5), params=params)
        assert_that(list(resp.json.keys()),
                    is_(['main_game',
                         'future_combination_win_ticket',
                         'set_numbers_by_parts', '4', '3', '2', '1']))

        assert_that(resp.json['main_game'], is_('5'))
        assert_that(len(resp.json['future_combination_win_ticket']),
                    is_(61))
        assert_that(len(set(resp.json['future_combination_win_ticket'])),
                    is_(61))
        assert_that(resp.json['set_numbers_by_parts'],
                    is_([1, 2, 5, 6, 9, 10, 11, 12, 14, 15, 16, 19, 22, 23, 25, 26, 32, 33, 34,
                         36, 38, 39, 40, 43, 46, 47, 48, 51, 52, 55, 64, 69, 70, 71, 72, 73, 75,
                         78, 79, 80, 82]))
        assert_that(resp.json['1'], is_([]))
        assert_that(resp.json['2'], is_([]))
        assert_that(resp.json['3'], is_([]))
        assert_that(resp.json['4'], is_([]))

    def test_part_consists_of(self):
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 1))
        GameFactory(amount_games=1, in_order_numbers=True)
        GameFactory(fields_games=get_fields_games(FNs.numbers_3, 3))

        params = {'parts_by_used': '2,3,6,8',
                  'add_numbers': '12,14',
                  'part_consists_of': '2'}

        resp = self.app.get(self._get_endpoint(4), params=params)
        assert_that(resp.json['1'], is_not([]))
        assert_that(resp.json['2'], is_([]))
        assert_that(resp.json['3'], is_not([]))

    def test_order_row(self):
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 1))
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 2))
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 3))

        params = {'parts_by_used': '1,2,3,4,5,6,7',
                  'add_numbers': '12,14',
                  'order_row': '30'}

        resp = self.app.get(self._get_endpoint(4), params=params)
        assert_that(resp.json['1'], is_not([]))
        assert_that(resp.json['2'], is_not([]))
        assert_that(resp.json['3'], is_not([]))

    def test_how_comparison_games(self):
        GameFactory(fields_games=get_fields_games(FNs.numbers_1, 1))
        GameFactory(fields_games=get_fields_games(FNs.numbers_2, 2))
        GameFactory(fields_games=get_fields_games(FNs.numbers_3, 3))

        params = {'parts_by_used': '2,3,6,8',
                  'add_numbers': '12,14',
                  'how_comparison_games': '2'}

        resp = self.app.get(self._get_endpoint(4), params=params)
        assert_that(list(resp.json.keys()),
                    is_(['main_game',
                         'future_combination_win_ticket',
                         'set_numbers_by_parts', '3', '2']))
