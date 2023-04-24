from django_webtest import WebTest
from hamcrest import assert_that, has_length, is_

from tests.helpers import GameFactory


class GameTestApiCase(WebTest):
    endpoint = '/test_lotto1/game/'

    def setUp(self):
        super(GameTestApiCase, self).setUp()
        self.game_factory = GameFactory()

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
        _factory = GameFactory(amount_games=1, numbers_in_lotto=90,
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
        _factory = GameFactory(amount_games=1, numbers_in_lotto=90,
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
        _factory = GameFactory(amount_games=1, numbers_in_lotto=90,
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
        _factory = GameFactory(amount_games=1, numbers_in_lotto=90,
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
        _factory = GameFactory(amount_games=1, numbers_in_lotto=90,
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
        assert_that([resp.json[0]['game_id'], resp.json[1]['game_id']], is_(['1', '3']))
