from random import randint, shuffle

from django_webtest import WebTest
from hamcrest import assert_that, is_

from lotto_app.app.management.command_utils import Probabilities8Add
from lotto_app.app.management.commands.command_8add import Command
from lotto_app.config import get_from_config
from tests.helpers import GameFactory8AddNumbers as GF8As


def get_fields_games(numbers, add_numbers, game_id):
    return [
        {'name_game': 'test_lotto2',
         'game_id': game_id,
         'numbers': numbers,
         'add_numbers': add_numbers
         }
    ]


def get_standart_game_obj(q=101):
    for i in range(1, q):
        _numbers = [n for n in range(1, 21)]
        shuffle(_numbers)
        GF8As(fields_games=get_fields_games(_numbers[0:8], [randint(1, 4)], i+100))


class Command8addCommandTest(WebTest):

    def preparation_data(self, q=101):
        get_standart_game_obj(q)

        c = Command()
        c.name_game = 'test_lotto2'
        c.numbers_in_lotto = 20
        c.gen_option = '3, 2, 2, 1'
        c.start_game_id = int(c._get_start_game_id())
        c.gen_probability = Probabilities8Add(c.name_game,
                                              c.start_game_id,
                                              100)
        c.max_add_number = 5
        c.steps_back_games = {
            '2': int(get_from_config('command_8add', 'two_steps_back_games')),
            '3': int(get_from_config('command_8add', 'three_steps_back_games'))
        }
        c.limit_overlap = {
            '2': int(get_from_config('command_8add', 'two_limit_overlap')),
            '3': int(get_from_config('command_8add', 'three_limit_overlap'))
        }
        c.limit_amount_seq = {
            '2': int(get_from_config('command_8add', 'two_limit_amount_seq')),
            '3': int(get_from_config('command_8add', 'three_limit_amount_seq'))
        }

        c.exclude_one_numbers = c._get_exclude_one_numbers()
        c.exclude_two_numbers = c._get_exclude_two_numbers()
        c.exclude_three_numbers = c._get_exclude_three_numbers()
        c.preferred_added_number = c._get_preferred_added_number()
        return c

    def test_command_pc_choice_numbers(self):
        c = self.preparation_data()
        pc_choice_numbers = c.pc_choice_numbers()
        assert_that(list(pc_choice_numbers.keys()), is_(['numbers', 'add_number']))
        assert_that(
            c.gen_probability._get_combination_options_8_add(pc_choice_numbers['numbers']),
            is_([3, 2, 2, 1])
        )

    def test_comparison_exclude_three_numbers(self):
        get_standart_game_obj(15)
        c = Command()
        c.name_game = 'test_lotto2'
        c.numbers_in_lotto = 20
        c.gen_option = '3, 2, 2, 1'
        c.start_game_id = int(c._get_start_game_id())

        c.exclude_three_numbers = [[1, 2, 3], [18, 19, 20]]
        # [3, 2, 1, 1, 1] - 2,3,4
        GF8As(fields_games=get_fields_games([2, 3, 4, 7, 8, 10, 12, 15],
                                            [randint(1, 4)], c.start_game_id + 1))
        # [5, 3] - 10,11,12
        GF8As(fields_games=get_fields_games([1, 2, 3, 4, 5, 10, 11, 12],
                                            [randint(1, 4)], c.start_game_id + 2))
        # Simple
        GF8As(fields_games=get_fields_games([1, 3, 5, 7, 9, 11, 13, 15],
                                            [randint(1, 4)], c.start_game_id + 3))
        # [4, 3, 1] - 9,10,11
        GF8As(fields_games=get_fields_games([1, 2, 3, 4, 9, 10, 11, 15],
                                            [randint(1, 4)], c.start_game_id + 4))
        c.start_game_id = int(c._get_start_game_id())
        c.gen_probability = Probabilities8Add(c.name_game,
                                              c.start_game_id,
                                              10)

        # [[1, 2, 3], [2,3,4], [10,11,12], [9,10,11], [18, 19, 20]]
        assert_that(
            c._comparison_exclude_three_numbers([4, 5, 6, 1, 2, 18, 14, 12],
                                                [[1, 2, 3], [18, 19, 20]]),
            is_(False)
        )
        assert_that(
            c._comparison_exclude_three_numbers([1, 2, 3, 5, 6, 18, 14, 12],
                                                [[1, 2, 3], [18, 19, 20]]),
            is_(True)
        )
        assert_that(
            c._comparison_exclude_three_numbers([2, 3, 4, 9, 6, 18, 14, 20],
                                                [[1, 2, 3], [18, 19, 20]]),
            is_(True)
        )
        assert_that(
            c._comparison_exclude_three_numbers([10, 11, 12, 1, 6, 18, 14, 20],
                                                [[1, 2, 3], [18, 19, 20]]),
            is_(True)
        )
        assert_that(
            c._comparison_exclude_three_numbers([9, 10, 11, 1, 6, 18, 14, 20],
                                                [[1, 2, 3], [18, 19, 20]]),
            is_(True)
        )
        assert_that(
            c._comparison_exclude_three_numbers([1, 14, 18, 19, 20, 2, 4, 10],
                                                [[1, 2, 3], [18, 19, 20]]),
            is_(True)
        )
