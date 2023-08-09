from django.test import TestCase
from django_webtest import WebTest
from hamcrest import assert_that, calling, has_length, is_, raises

from lotto_app.app.models import Game
from lotto_app.app.views.games import GameViewSet
from tests.helpers import GameFactory8AddNumbers, GameFactory90


class Game90TestApiCase(WebTest):
    endpoint = '/test_lotto1/game/'

    def setUp(self):
        super(Game90TestApiCase, self).setUp()
        self.game_factory = GameFactory90()

    def test_happy_path_get_list(self):
        resp = self.app.get(self.endpoint)
        assert_that(resp.json, has_length(3))
        assert_that(resp.json[1]['game_id'], is_('2'))
        assert_that(resp.json[0]['numbers'], has_length(87))
        assert_that(resp.json[2]['no_numbers'], has_length(3))

    def test_happy_path_get(self):
        resp = self.app.get(f'{self.endpoint}2/')
        assert_that(resp.json['game_id'], is_('2'))
        assert_that(resp.json['numbers'], has_length(87))
        assert_that(resp.json['no_numbers'], has_length(3))

    def test_happy_path_post(self):
        _factory = GameFactory90(amount_games=1, numbers_in_lotto=90,
                                 no_numbers_in_lotto=4, only_games_json=True)
        params = _factory.get_game_json()
        resp = self.app.post_json(self.endpoint, params=params)
        assert_that(resp.json['game_id'], is_('4'))
        assert_that(resp.json['numbers'], has_length(86))
        assert_that(resp.json['no_numbers'], has_length(4))
        assert_that(resp.json['win_card']['by_account'], is_(36))
        assert_that(resp.json['win_card']['last_win_number_card'],
                    is_(params['last_win_number_card']))
        assert_that(resp.json['win_ticket']['by_account'], is_(61))
        assert_that(resp.json['win_ticket']['last_win_number_ticket'],
                    is_(params['last_win_number_ticket']))

    def test_happy_path_str_numbers_post(self):
        _factory = GameFactory90(amount_games=1, numbers_in_lotto=90,
                                 no_numbers_in_lotto=4, only_games_json=True)
        params = _factory.get_game_str_numbers_json()
        resp = self.app.post_json(self.endpoint, params=params)
        assert_that(resp.json['game_id'], is_('4'))
        assert_that(resp.json['numbers'], has_length(86))
        assert_that(resp.json['no_numbers'], has_length(4))
        assert_that(resp.json['win_card']['by_account'], is_(36))
        assert_that(resp.json['win_card']['last_win_number_card'],
                    is_(params['last_win_number_card']))
        assert_that(resp.json['win_ticket']['by_account'], is_(61))
        assert_that(resp.json['win_ticket']['last_win_number_ticket'],
                    is_(params['last_win_number_ticket']))

    def test_happy_path_post_without_win(self):
        _factory = GameFactory90(amount_games=1, numbers_in_lotto=90,
                                 no_numbers_in_lotto=4, only_games_json=True)
        _params = _factory.get_game_json()
        resp = self.app.post_json(self.endpoint,
                                  params={'name_game': 'test_lotto1',
                                          'game_id': _params['game_id'],
                                          'numbers': _params['numbers']})
        assert_that(resp.json['game_id'], is_('4'))
        assert_that(resp.json['numbers'], has_length(86))
        assert_that(resp.json['no_numbers'], has_length(4))
        assert_that(resp.json['win_card']['by_account'], is_(None))
        assert_that(resp.json['win_card']['last_win_number_card'], is_(None))
        assert_that(resp.json['win_ticket']['by_account'], is_(None))
        assert_that(resp.json['win_ticket']['last_win_number_ticket'], is_(None))

    def test_happy_path_post_auto_win(self):
        _factory = GameFactory90(amount_games=1, numbers_in_lotto=90,
                                 no_numbers_in_lotto=2, only_games_json=True)
        params = _factory.get_game_auto_win_json()
        dirty_numbers = [num for num in params['str_numbers'].replace(' ', ',').split(',') if num]
        last_win_number_card = int(dirty_numbers[1][-2:])
        last_win_number_ticket = int(dirty_numbers[2][-2:])
        resp = self.app.post_json(self.endpoint, params=params)
        assert_that(resp.json['game_id'], is_('4'))
        assert_that(resp.json['numbers'], has_length(88))
        assert_that(resp.json['no_numbers'], has_length(2))
        assert_that(resp.json['win_card']['by_account'], is_(37))
        assert_that(resp.json['win_card']['last_win_number_card'], is_(last_win_number_card))
        assert_that(resp.json['win_ticket']['by_account'], is_(62))
        assert_that(resp.json['win_ticket']['last_win_number_ticket'], is_(last_win_number_ticket))

    def test_happy_path_put(self):
        _factory = GameFactory90(amount_games=1, numbers_in_lotto=90,
                                 no_numbers_in_lotto=60, only_games_json=True)
        params = _factory.get_game_auto_win_json()
        resp_get = self.app.get(f'{self.endpoint}1/')
        resp = self.app.put_json(f'{self.endpoint}1/', params={'name_game': 'test_lotto1',
                                                               'game_id': '1',
                                                               'str_numbers': params['str_numbers']})
        assert_that(resp.json['game_id'], is_('1'))
        assert_that(resp.json['numbers'], has_length(30))
        assert_that(resp.json['no_numbers'], has_length(3))

        last_win_number_card = resp_get.json['win_card']['last_win_number_card']
        last_win_number_ticket = resp_get.json['win_ticket']['last_win_number_ticket']
        assert_that(resp.json['win_card']['last_win_number_card'], is_(last_win_number_card))
        assert_that(resp.json['win_ticket']['last_win_number_ticket'],
                    is_(last_win_number_ticket))

        if last_win_number_card in resp.json['numbers']:
            assert_that(resp.json['win_card']['by_account'],
                        is_(resp.json['numbers'].index(last_win_number_card) + 1))
        else:
            assert_that(resp.json['win_card']['by_account'], is_(30))

        if last_win_number_ticket in resp.json['numbers']:
            assert_that(resp.json['win_ticket']['by_account'],
                        is_(resp.json['numbers'].index(last_win_number_ticket) + 1))
        else:
            assert_that(resp.json['win_ticket']['by_account'], is_(30))

    def test_happy_path_patch(self):
        resp_get = self.app.get(f'{self.endpoint}3/')

        numbers = resp_get.json['numbers']
        no_numbers = resp_get.json['no_numbers']

        resp = self.app.patch_json(f'{self.endpoint}3/',
                                   params={'last_win_number_card': numbers[5],
                                           'last_win_number_ticket': numbers[10]})
        assert_that(resp.json['game_id'], is_('3'))
        assert_that(resp.json['numbers'], is_(numbers))
        assert_that(resp.json['no_numbers'], is_(no_numbers))

        assert_that(resp.json['win_card']['by_account'], is_(6))
        assert_that(resp.json['win_ticket']['by_account'], is_(11))

        assert_that(resp.json['win_card']['last_win_number_card'], is_(numbers[5]))
        assert_that(resp.json['win_ticket']['last_win_number_ticket'], is_(numbers[10]))

    def test_happy_path_delete(self):
        resp = self.app.get(self.endpoint)
        assert_that(resp.json, has_length(3))

        resp = self.app.delete(f'{self.endpoint}2/')
        assert_that(resp.status, is_('204 No Content'))

        resp = self.app.get(self.endpoint)
        assert_that(resp.json, has_length(2))
        assert_that([resp.json[0]['game_id'], resp.json[1]['game_id']], is_(['3', '1']))


class GetSeveralGamesInfoTest(TestCase):

    def expected_several_games_info(self):
        total_cost_numbers = {88: 0, 89: 0, 90: 0}
        v = 18
        for i in range(87, 0, -1):
            v += 6
            total_cost_numbers.update({i: v})
        return {
            'min_cost': {88: 0},
            'max_cost': {1: 540},
            'total_cost_numbers': total_cost_numbers,
        }

    def test_validate_not_enough_games(self):
        GameFactory90(amount_games=1)
        assert_that(
            calling(GameViewSet.get_several_games_info).with_args(
                'test_lotto1', 1),
            raises(IndexError))
        GameFactory90(amount_games=1)
        assert_that(
            calling(GameViewSet.get_several_games_info).with_args(
                'test_lotto1', 2),
            raises(IndexError))

        # happy_path get_several_games_info
        GameFactory90(amount_games=1)
        assert_that(Game.objects.count(), is_(3))
        assert_that(list(GameViewSet.get_several_games_info('test_lotto1', 3).keys()),
                    is_(['min_cost', 'max_cost', 'total_cost_numbers', '9_parts_numbers']))

    def test_happy_path_get_several_games_info(self):
        GameFactory90(amount_games=3, in_order_numbers=True)
        assert_that(Game.objects.count(), is_(3))
        info = GameViewSet.get_several_games_info('test_lotto1', 3)
        expected_resp = self.expected_several_games_info()
        assert_that(info['min_cost'], is_(expected_resp['min_cost']))
        assert_that(info['max_cost'], is_(expected_resp['max_cost']))
        assert_that(info['total_cost_numbers'], is_(expected_resp['total_cost_numbers']))
        assert_that(info['9_parts_numbers'],
                    is_({0: [88, 89, 90, 87, 86, 85, 84, 83, 82, 81],
                         1: [80, 79, 78, 77, 76, 75, 74, 73, 72, 71],
                         2: [70, 69, 68, 67, 66, 65, 64, 63, 62, 61],
                         3: [60, 59, 58, 57, 56, 55, 54, 53, 52, 51],
                         4: [50, 49, 48, 47, 46, 45, 44, 43, 42, 41],
                         5: [40, 39, 38, 37, 36, 35, 34, 33, 32, 31],
                         6: [30, 29, 28, 27, 26, 25, 24, 23, 22, 21],
                         7: [20, 19, 18, 17, 16, 15, 14, 13, 12, 11],
                         8: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]}))

    def test_happy_path_without_field_last_wins(self):
        GameFactory90(amount_games=2, in_order_numbers=True)
        _fields_games = GameFactory90(amount_games=1,
                                      only_games_json=True).get_game_json()
        GameFactory90(fields_games=[{
            'name_game': _fields_games['name_game'],
            'game_id': _fields_games['game_id'],
            'numbers': _fields_games['numbers'],
            'no_numbers': _fields_games['no_numbers']
        }])
        GameFactory90(amount_games=1, in_order_numbers=True)
        assert_that(Game.objects.count(), is_(4))
        info = GameViewSet.get_several_games_info('test_lotto1', 4)
        expected_resp = self.expected_several_games_info()
        assert_that(info['min_cost'], is_(expected_resp['min_cost']))
        assert_that(info['max_cost'], is_(expected_resp['max_cost']))
        assert_that(info['total_cost_numbers'], is_(expected_resp['total_cost_numbers']))


class FutureGame30Test(WebTest):
    endpoint = '/test_lotto1/game/'

    def setUp(self):
        super(FutureGame30Test, self).setUp()

    def test_happy_path_future_game_30(self):
        GameFactory90(amount_games=4, in_order_numbers=True)
        params = {'good_games': 3,
                  'bad_games': 3}
        resp = self.app.get(f'{self.endpoint}4/future_game_30/', params=params)
        assert_that(list(resp.json.keys()),
                    is_(['current_index_bingo', 'index_9_parts', 'good_numbers', 'bad_numbers']))
        assert_that(resp.json['current_index_bingo'], is_(9480))
        assert_that(resp.json['index_9_parts'],
                    is_({'0': 2, '1': 3, '2': 3, '3': 3, '4': 3, '5': 3, '6': 4, '7': 4, '8': 5}))
        assert_that(resp.json['good_numbers'],
                    is_([i for i in range(61, 91)]))
        assert_that(resp.json['bad_numbers'],
                    is_([i for i in range(1, 61)]))


class CombinationWinTicketTest(WebTest):
    endpoint = '/test_lotto1/game/'

    def _get_parts_numbers(self, part_consists_of, combination_numbers):
        parts = []
        i = 0
        for _ in combination_numbers:
            if (len(combination_numbers) - i - part_consists_of) < 0:
                break
            parts.append(list(combination_numbers)[i:i+part_consists_of])
            i += 1
        return parts

    def test_happy_path_combination_win_ticket(self):
        GameFactory90(amount_games=1, in_order_numbers=True)
        params = {'part_consists_of': 5,
                  'order_row': 8}
        resp = self.app.get(f'{self.endpoint}1/combination_win_ticket/', params=params)
        assert_that(list(resp.json.keys()),
                    is_(['combination_win_ticket', 'parts', 'numbers_in_row']))
        assert_that(resp.json['combination_win_ticket'],
                    is_([i for i in range(1, 61)]))
        assert_that(resp.json['parts'],
                    is_(self._get_parts_numbers(params['part_consists_of'],
                                                resp.json['combination_win_ticket'])))
        assert_that(resp.json['numbers_in_row'],
                    is_([[i for i in range(1, 61)]]))


class Game8AddNumbersTestApiCase(WebTest):
    endpoint = '/test_lotto2/game/'

    def test_happy_path_get(self):
        GameFactory8AddNumbers(amount_games=2)
        resp = self.app.get(f'{self.endpoint}2/')
        assert_that(resp.json['game_id'], is_('2'))
        assert_that(resp.json['numbers'], has_length(8))
        assert_that(resp.json['no_numbers'], is_(None))
        assert_that(resp.json['win_card'], is_({'last_win_number_card': None, 'by_account': None}))
        assert_that(resp.json['win_ticket'], is_({'last_win_number_ticket': None, 'by_account': None}))
        assert_that(resp.json['add_numbers'], has_length(1))
        assert_that(list(resp.json.keys()),
                    is_(['name_game', 'game_id', 'numbers', 'no_numbers', 'win_card',
                         'win_ticket', 'add_numbers']))

    def test_happy_path_post(self):
        _factory = GameFactory8AddNumbers(only_games_json=True)
        params = _factory.get_game_json()
        resp = self.app.post_json(self.endpoint, params=params)
        assert_that(resp.json['game_id'], is_('1'))
        assert_that(resp.json['numbers'], has_length(8))
        assert_that(resp.json['no_numbers'], is_(None))
        assert_that(resp.json['win_card'], is_({'last_win_number_card': None, 'by_account': None}))
        assert_that(resp.json['win_ticket'], is_({'last_win_number_ticket': None, 'by_account': None}))
        assert_that(resp.json['add_numbers'], has_length(1))
        assert_that(list(resp.json.keys()),
                    is_(['name_game', 'game_id', 'numbers', 'no_numbers', 'win_card',
                         'win_ticket', 'add_numbers']))
