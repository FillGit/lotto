from django_webtest import WebTest
from hamcrest import assert_that, calling, contains_inanyorder, is_, raises
from webtest.app import AppError

from lotto_app.app.management.command_utils import Probabilities8Add, Probabilities8AddOneNumber
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


def get_standart_game_obj(game_ids=[1, 2, 3, 4, 5]):
    GF8As(fields_games=get_fields_games(F8Ns.numbers_1, [1], game_ids[0]))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_2, [2], game_ids[1]))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_3, [3], game_ids[2]))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_4, [4], game_ids[3]))
    GF8As(fields_games=get_fields_games(F8Ns.numbers_5, [4], game_ids[4]))


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


class InfoSequenceTest(WebTest):

    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/info_sequence/'

    def _standart_game_obj(self):
        get_standart_game_obj()
        get_standart_game_obj([6, 7, 8, 9, 10])
        get_standart_game_obj([13, 11, 14, 12, 15])

    def test_happy_path_info_sequence_without_only_len_sequence(self):
        self._standart_game_obj()
        params = {'how_games': 15,
                  'sequence': '14,15,16',
                  'only_len_sequence': 0}

        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_([{'11': '11', 'previous game_id': '15', 'difference': 4},
                         {'7': '7', 'previous game_id': '11', 'difference': 4},
                         {'2': '2', 'previous game_id': '7', 'difference': 5},
                         {'min_difference': 4,
                          'middle_difference': 4.333333333333333,
                          'max_difference': 5,
                          'median': 4,
                          'amount_sequence': 3}]))

    def test_happy_path_info_sequence_with_only_len_sequence(self):
        self._standart_game_obj()
        params = {'how_games': 15,
                  'sequence': '14,15,16',
                  'only_len_sequence': 1
                  }
        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json, is_([{'amount_sequence': 0}]))

        params['sequence'] = '9,10,11'
        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_([{'13': '13', 'previous game_id': '15', 'difference': 2},
                         {'6': '6', 'previous game_id': '13', 'difference': 7},
                         {'1': '1', 'previous game_id': '6', 'difference': 5},
                         {'min_difference': 2,
                          'middle_difference': 4.666666666666667,
                          'max_difference': 7,
                          'median': 5,
                          'amount_sequence': 3}]))

    def test_happy_path_info_sequence_how_info_games(self):
        self._standart_game_obj()
        params = {'how_games': 15,
                  'sequence': '14,15,16',
                  'how_info_games': 10}

        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_([{'11': '11', 'previous game_id': '15', 'difference': 4},
                         {'7': '7', 'previous game_id': '11', 'difference': 4},
                         {'min_difference': 4,
                          'middle_difference': 4,
                          'max_difference': 4,
                          'median': 4.0,
                          'amount_sequence': 2}]))

    def test_validate_sequence(self):
        get_standart_game_obj()
        params = {'how_games': 5,
                  'sequence': '13,15'}
        assert_that(calling(self.app.get).with_args(self._get_endpoint(5), params=params),
                    raises(AppError))


class AllSequencesInGamesTest(WebTest):
    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/all_sequences_in_games/'

    def _standart_game_obj(self):
        get_standart_game_obj()
        get_standart_game_obj([6, 7, 8, 9, 10])
        get_standart_game_obj([13, 11, 14, 12, 15])

    def test_happy_path_info_all_sequences_in_games_1(self):
        self._standart_game_obj()
        params = {'how_games': 15,
                  'part_consists_of': 1,
                  'how_info_games': 10}

        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_({'[1]': 2, '[2]': 8, '[3]': 6, '[4]': 4, '[5]': 6, '[6]': 4,
                         '[7]': 2, '[8]': 4, '[9]': 2, '[10]': 6, '[11]': 4, '[12]': 4,
                         '[13]': 6, '[14]': 2, '[15]': 4, '[16]': 2, '[17]': 4,
                         '[18]': 2, '[19]': 2, '[20]': 6}))

    def test_happy_path_info_all_sequences_in_games_3(self):
        self._standart_game_obj()
        params = {'how_games': 15,
                  'part_consists_of': 3,
                  'how_info_games': 10}

        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_({'[1, 2, 3]': 0, '[2, 3, 4]': 2, '[3, 4, 5]': 2, '[4, 5, 6]': 0,
                         '[5, 6, 7]': 2, '[6, 7, 8]': 2, '[7, 8, 9]': 0, '[8, 9, 10]': 0,
                         '[9, 10, 11]': 2, '[10, 11, 12]': 0, '[11, 12, 13]': 2,
                         '[12, 13, 14]': 2, '[13, 14, 15]': 2, '[14, 15, 16]': 2,
                         '[15, 16, 17]': 0, '[16, 17, 18]': 0, '[17, 18, 19]': 0,
                         '[18, 19, 20]': 0}))


class ProbabilitySequencesTest(WebTest):
    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/probability_sequences/'

    def _standart_game_obj(self):
        get_standart_game_obj()
        get_standart_game_obj([6, 7, 8, 9, 10])
        get_standart_game_obj([13, 11, 14, 12, 15])

    def test_happy_path_probability_sequences(self):
        self._standart_game_obj()
        params = {'how_games': 10,
                  'part_consists_of': 3,
                  'steps_back_games': 5,
                  'limit_overlap': 2,
                  'limit_amount_seq': 2,
                  }

        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_({'12': {'ids': ['11', '10', '9', '8', '7'],
                                'exceeding_limit_overlap': {'[11, 12, 13]': 2,
                                                            '[12, 13, 14]': 2,
                                                            '[13, 14, 15]': 2,
                                                            '[14, 15, 16]': 2},
                                'numbers_have': []},
                         'check_games': 10,
                         'exceeding_limit_overlap': 1,
                         'numbers_have': 0}))


class ComparisonLastGameTest(WebTest):
    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/comparison_last_game/'

    def test_comparison_last_game(self):
        get_standart_game_obj([111, 112, 113, 114, 115])
        params = {'how_games': 5}

        resp = self.app.get(self._get_endpoint(115), params=params)
        assert_that(resp.json,
                    is_({'115': 4,
                         '114': 3,
                         '113': 0,
                         '112': 1,
                         '0': 1, '1': 1, '2': 0, '3': 1, '4': 1, '5': 0, '6': 0, '7': 0, '8': 0}))


class ProbabilityOneNumberTest(WebTest):
    def _get_endpoint(self, game_id):
        return f'/test_lotto2/research_8_add/{game_id}/probability_one_number/'

    def _standart_game_obj(self):
        get_standart_game_obj()
        get_standart_game_obj([6, 7, 8, 9, 10])
        get_standart_game_obj([13, 11, 14, 12, 15])

    def test_happy_path_probability_one_number(self):
        self._standart_game_obj()
        params = {'how_games': 6,
                  'steps_back_games_previous': 3,
                  'steps_back_games_small': 3,
                  'steps_back_games_big': 5,
                  }

        resp = self.app.get(self._get_endpoint(15), params=params)
        assert_that(resp.json,
                    is_({'15': {'obj.numbers': [20, 17, 2, 5, 13, 3, 4, 12],
                                'set_one_numbers': [2],
                                'set_one_numbers_by_previous': [2, 10],
                                'numbers_have': 1},
                        '11': {'obj.numbers': [14, 15, 12, 11, 4, 19, 13, 16],
                               'set_one_numbers': [2],
                               'set_one_numbers_by_previous': [2],
                               'numbers_have': 0},
                         'check_games': 6,
                         'len_set_one_numbers': 2,
                         'numbers_have': 1,
                         'probability': 0.5}))

    def test_probability_one_number_one_number_empty(self):
        [GF8As(fields_games=get_fields_games(F8Ns.numbers_1, [1], i)) for i in range(1, 8)]
        params = {'how_games': 2,
                  'steps_back_games_previous': 1,
                  'steps_back_games_small': 2,
                  'steps_back_games_big': 4,
                  }

        resp = self.app.get(self._get_endpoint(7), params=params)
        assert_that(resp.json,
                    is_({'check_games': 2,
                         'len_set_one_numbers': 0,
                         'numbers_have': 0,
                         'probability': 0}))

    def test_get_probability_one_number(self):
        self._standart_game_obj()

        def _data_expect(previous_id):
            _one_number = Probabilities8AddOneNumber()
            gen_probability = Probabilities8Add('test_lotto2', 14, 14)
            return _one_number.get_probability_one_number(
                    'test_lotto2', previous_id,
                    3,
                    3,
                    3,
                    gen_probability
                )

        assert_that(_data_expect(14), is_(({2, 10}, {2})))
        assert_that(_data_expect(13), is_((set(), set())))
        assert_that(_data_expect(12), is_(({13}, set())))
        assert_that(_data_expect(11), is_(({13}, set())))
        assert_that(_data_expect(10), is_(({2}, {2})))
        assert_that(_data_expect(9), is_((set(), set())))

    def test_validate_probability_one_number(self):
        get_standart_game_obj()
        params = {'how_games': 4,
                  'steps_back_games_previous': 2,
                  'steps_back_games_small': 1,
                  'steps_back_games_big': 3,
                  }
        assert_that(calling(self.app.get).with_args(self._get_endpoint(5), params=params),
                    raises(AppError))
