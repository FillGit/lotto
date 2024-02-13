import time
from datetime import datetime, timedelta
from random import shuffle

import pytz
import requests
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import IntegerField
from django.db.models.functions import Cast

from lotto_app.app.management.command_utils import Probabilities8Add
from lotto_app.app.models import Game
from lotto_app.app.parsers.choise_parsers import ChoiseParsers
from lotto_app.app.utils import sort_numbers, str_to_list_of_int
from lotto_app.config import get_from_config
from lotto_app.constants import COMBINATION_OPTIONS_8_ADD


def get_one_number_factors():
    draft_list = get_from_config('command_8add', 'one_number_factors').split('] [')
    one_number_factors = []
    for s in draft_list:
        factors = str(s).replace(' ', '').replace('[', '').replace(']', '').split(',')
        one_number_factors.append(
            {
                'steps_back_games_previous': int(factors[0]),
                'steps_back_games_small': int(factors[1]),
                'steps_back_games_big': int(factors[2])
            })
    return one_number_factors


class Command(BaseCommand):
    SEND_EMAIL = get_from_config('send_email', 'send_email')
    EMAIL_HOST_USER = get_from_config('send_email', 'email_host_user')

    help = 'Show to make command_8add'

    def init_before_cycle(self, *args, **kwargs):
        self.my_host = get_from_config('lotto_url', 'my_host')
        self.name_game = kwargs['name_game']
        self.numbers_in_lotto = int(get_from_config('lotto_8_add',
                                                    f'numbers_in_lotto_{self.name_game}'))
        self.cycle_range = 10
        if kwargs['cycle_range']:
            self.cycle_range = kwargs['cycle_range']

        self.expected_print_error_command = get_from_config('command_8add',
                                                            'expected_print_error_command')
        self.old_game_id = self._get_start_game_id()
        self.sleep_cycle = None
        self.gen_probability = None
        self.gen_option = str(get_from_config('command_8add', 'gen_option'))
        self.exclude_one_numbers = []
        self.exclude_two_numbers = []
        self.exclude_three_numbers = []
        self.options_last_games = None
        self.max_add_number = int(get_from_config('command_8add', 'max_add_number'))
        self.info_evaluate_future_game = {}

        self.steps_back_games = {
            '1': int(get_from_config('command_8add', 'one_steps_back_games')),
            '2': int(get_from_config('command_8add', 'two_steps_back_games')),
            '3': int(get_from_config('command_8add', 'three_steps_back_games')),
            'options_steps_back_co': int(get_from_config('command_8add',
                                                         'options_steps_back_combination_option')),
        }
        self.limit_overlap = {
            '1': int(get_from_config('command_8add', 'one_limit_overlap')),
            '2': int(get_from_config('command_8add', 'two_limit_overlap')),
            '3': int(get_from_config('command_8add', 'three_limit_overlap'))
        }
        self.limit_amount_seq = {
            '1': int(get_from_config('command_8add', 'one_limit_amount_seq')),
            '2': int(get_from_config('command_8add', 'two_limit_amount_seq')),
            '3': int(get_from_config('command_8add', 'three_limit_amount_seq'))
        }
        self.stdout.write(f"Name game: {self.name_game}")
        self.stdout.write(f"cycle_range: {self.cycle_range}")

    def _get_start_game_id(self):
        return Game.objects.filter(name_game=self.name_game).annotate(
            game_id_int=Cast('game_id', output_field=IntegerField())).last().game_id

    def _get_resp_command(self):
        class_parser = ChoiseParsers(f'{self.name_game}_command', '').get_class_parser()
        return class_parser.parser_response_for_view()

    def get_connects(self):
        resp_command = self._get_resp_command()
        if self.expected_print_error_command in resp_command['draft_data']:
            return resp_command

        if resp_command['game_id'] == self.old_game_id:
            return resp_command

        if int(resp_command['game_id']) == int(self.old_game_id)+1:
            self.stdout.write('name_game/parsers/parsers/')
            requests.post(f'{self.my_host}/{self.name_game}/parsers/parsers/',
                          json={'page': int(self.old_game_id) + 1})
            return resp_command

        if int(resp_command['game_id']) > int(self.old_game_id)+1:
            self.stdout.write('name_game/parsers/parsers_mult_pages/')
            requests.post(f'{self.my_host}/{self.name_game}/parsers/parsers_mult_pages/',
                          json={
                              'page_start': int(self.old_game_id) + 1,
                              'page_end': int(resp_command['game_id'])
                          })
            return resp_command

    def get_sleep_cycle(self, time_now, resp_command):
        try:
            if self.expected_print_error_command in resp_command['draft_data']:
                self.stdout.write('Данные загружаются на сайт')
                return True, 120
        except TypeError:
            print(resp_command)
            return True, 90

        time_command = resp_command['time_em']
        time_15 = time_command + timedelta(minutes=15)
        if resp_command['game_id'] == self.old_game_id and (time_now - time_15).total_seconds() > 0:
            return True, 300
        return False, (time_15 - time_now).total_seconds()+120

    def _get_exclude_group_numbers(self, part_consists_of, steps_back_games,
                                   limit_overlap, limit_amount_seq):
        exceeding_limit_overlap, _ = self.gen_probability.get_exceeding_limit_overlap(
            self.name_game, self.start_game_id,
            part_consists_of, steps_back_games,
            limit_overlap, self.gen_probability
        )
        return [str_to_list_of_int(seq) for seq in exceeding_limit_overlap] if exceeding_limit_overlap and len(
            exceeding_limit_overlap.keys()) >= limit_amount_seq else []

    def _get_exclude_one_numbers(self):
        return self._get_exclude_group_numbers(1,
                                               self.steps_back_games['1'],
                                               self.limit_overlap['1'],
                                               self.limit_amount_seq['1'])

    def _get_exclude_two_numbers(self):
        return self._get_exclude_group_numbers(2,
                                               self.steps_back_games['2'],
                                               self.limit_overlap['2'],
                                               self.limit_amount_seq['2'])

    def _get_exclude_three_numbers(self):
        return self._get_exclude_group_numbers(3,
                                               self.steps_back_games['3'],
                                               self.limit_overlap['3'],
                                               self.limit_amount_seq['3'])

    def _get_info_evaluate_future_game(self):
        info_evaluate_future_game = {
            'exclude_one_numbers': self.exclude_one_numbers,
            'exclude_two_numbers': self.exclude_two_numbers,
            'exclude_three_numbers': self.exclude_three_numbers,
            'options_last_games': self.options_last_games,
        }
        print(self.print_info(info_evaluate_future_game))
        return info_evaluate_future_game

    def _update_info_evaluate_future_game(self):
        self.info_evaluate_future_game['update_one'] = {}
        for obj in self.gen_probability.game_objs:
            if int(obj.game_id) > self.start_game_id-30:
                _id = int(obj.game_id)-1
                exceeding_limit_overlap, game_objs = self.gen_probability.get_exceeding_limit_overlap(
                    self.name_game, _id,
                    1, self.steps_back_games['1'],
                    self.limit_overlap['1'], self.gen_probability
                )

                if exceeding_limit_overlap and len(exceeding_limit_overlap.keys()) >= self.limit_amount_seq['1']:
                    self.info_evaluate_future_game['update_one'].update({obj.game_id: {
                        'exceeding_limit_overlap': exceeding_limit_overlap,
                        'numbers_have': [
                            seq for seq in exceeding_limit_overlap
                            if set(str_to_list_of_int(seq)).issubset(set(obj.numbers))
                        ]}})

        self.info_evaluate_future_game['update_two'] = {}
        for obj in self.gen_probability.game_objs:
            if int(obj.game_id) > self.start_game_id-30:
                _id = int(obj.game_id)-1
                exceeding_limit_overlap, game_objs = self.gen_probability.get_exceeding_limit_overlap(
                    self.name_game, _id,
                    2, self.steps_back_games['2'],
                    self.limit_overlap['2'], self.gen_probability
                )

                if exceeding_limit_overlap and len(exceeding_limit_overlap.keys()) >= self.limit_amount_seq['2']:
                    self.info_evaluate_future_game['update_two'].update({obj.game_id: {
                        'exceeding_limit_overlap': exceeding_limit_overlap,
                        'numbers_have': [
                            seq for seq in exceeding_limit_overlap
                            if set(str_to_list_of_int(seq)).issubset(set(obj.numbers))
                        ]}})

    def _init_future_game(self):
        self.start_game_id = int(self._get_start_game_id())
        self.gen_probability = Probabilities8Add(self.name_game,
                                                 self.start_game_id,
                                                 int(get_from_config('command_8add', 'how_games')))
        self.options_last_games = [
            self.gen_probability._get_combination_options_8_add(_obj.numbers)
            for _obj in self.gen_probability.game_objs[0:self.steps_back_games['options_steps_back_co']]
        ]

        self.exclude_one_numbers = self._get_exclude_one_numbers()
        self.exclude_two_numbers = self._get_exclude_two_numbers()
        self.exclude_three_numbers = self._get_exclude_three_numbers()
        self.info_evaluate_future_game = self._get_info_evaluate_future_game()

    def _reason_exclude_two_numbers_and_options(self, list_have_one, list_have_two):
        if self.exclude_two_numbers and self.exclude_one_numbers and (
           len([opt for opt in self.options_last_games
                if opt != COMBINATION_OPTIONS_8_ADD[self.gen_option]]) == self.steps_back_games['options_steps_back_co']
           ) and len([numbers_have for numbers_have in list_have_two[0:2] if numbers_have]) == 2 and (
               len([numbers_have for numbers_have in list_have_one[0:3] if numbers_have]) == 3
           ):
            self.info_evaluate_future_game['reason_for_choice'] = 'reason_exclude_two_numbers_and_options'
            return True
        return False

    def _reason_exclude_three_numbers(self, list_have_one, list_have_two):
        if self.exclude_three_numbers and self.exclude_two_numbers and self.exclude_one_numbers and (
           len([opt for opt in self.options_last_games[0:4]
                if opt != COMBINATION_OPTIONS_8_ADD['3, 2, 1, 1, 1']]) == 4
           ) and len([numbers_have for numbers_have in list_have_two[0:2] if numbers_have]) == 2 and (
               len([numbers_have for numbers_have in list_have_one[0:3] if numbers_have]) == 3
           ):
            self.info_evaluate_future_game['reason_for_choice'] = 'reason_exclude_three_numbers'
            return True
        return False

    def evaluate_future_game(self):
        self._init_future_game()
        self._update_info_evaluate_future_game()
        list_have_one = [v['numbers_have'] for _, v in self.info_evaluate_future_game['update_one'].items()]
        list_have_two = [v['numbers_have'] for _, v in self.info_evaluate_future_game['update_two'].items()]
        print('list_have_one', list_have_one)
        print('list_have_two', list_have_two)
        if (self._reason_exclude_two_numbers_and_options(list_have_one, list_have_two) or
                self._reason_exclude_three_numbers(list_have_one, list_have_two)):
            return True

        self.old_game_id = self.start_game_id
        return False

    def _comparison_combination_options(self, future_game_numbers):
        sort_numbers = self.gen_probability._get_combination_options_8_add(future_game_numbers)
        if self.info_evaluate_future_game['reason_for_choice'] == 'reason_exclude_three_numbers':
            if sort_numbers == COMBINATION_OPTIONS_8_ADD['3, 2, 1, 1, 1']:
                return False
        elif sort_numbers == COMBINATION_OPTIONS_8_ADD[self.gen_option]:
            return False
        return True

    def _comparison_current_game(self, future_game_numbers, current_game_numbers):
        _comparison = len(set(future_game_numbers) & set(current_game_numbers))
        if _comparison < 2:
            return True
        if _comparison > 4:
            return True
        return False

    def _comparison_exclude_two_numbers(self, future_game_numbers, exclude_numbers):
        for group in exclude_numbers:
            if set(future_game_numbers).issuperset(group):
                return True
        return False

    def _get_three_objs_for_comparison(self):
        three_objs = []
        for _obj in self.gen_probability.game_objs:
            _options = self.gen_probability._get_combination_options_8_add(_obj.numbers)
            if _options[0] == 3 or _options[0:2] == [4, 3] or _options[0:2] == [5, 3]:
                three_objs.append(_obj)
            if _options[0:3] == [3, 2, 1]:
                three_objs.append(_obj)
                break
        return three_objs

    def _get_three_numbers_for_comparison(self, three_objs):
        three_numbers = []
        for _obj in three_objs:
            numbers = list(set(_obj.numbers))
            i = 0
            for n in numbers[0:6]:
                if numbers[i+1] == n+1 and numbers[i+2] == n+2 and ((i+3 > 7) or numbers[i+3] != n+3):
                    three_numbers.append([n, n+1, n+2])
                i += 1
        return three_numbers

    def _comparison_exclude_three_numbers(self, future_game_numbers, exclude_numbers: list):
        three_objs = self._get_three_objs_for_comparison()
        three_numbers = self._get_three_numbers_for_comparison(three_objs)
        exclude_numbers.extend(three_numbers)
        for group in exclude_numbers:
            if set(future_game_numbers).issuperset(group):
                return True
        return False

    def _comparison_all_game_numbers(self, future_game_numbers):
        for _obj in self.gen_probability.game_objs:
            set_common_numbers = set(future_game_numbers) & set(_obj.numbers)
            if len(set_common_numbers) == 8:
                return True
        return False

    def _future_add_number(self):
        steps_back_games = 25
        _p8add = Probabilities8Add(
            self.name_game, self.start_game_id, steps_back_games,
            game_objs=self.gen_probability._get_probability_objs(self.start_game_id,
                                                                 steps_back_games,
                                                                 self.gen_probability.game_objs)
        )
        list_add_items = [_obj.add_numbers[0] for _obj in _p8add.game_objs]
        _sort_numbers = sort_numbers(list_add_items, 1, 4, True)
        if len({_obj.add_numbers[0] for _obj in _p8add.game_objs[:3]}) == 1:
            return _sort_numbers[0] if _sort_numbers[0] != _p8add.game_objs[0].add_numbers[0] else _sort_numbers[1]

        _a = [_sort_numbers[1], _sort_numbers[2], _sort_numbers[3]]
        shuffle(_a)
        return _sort_numbers[0] if list_add_items.count(_sort_numbers[0]) < steps_back_games/2 else _a[0]

    def pc_choice_numbers(self):
        _eons = [i[0] for i in self.exclude_one_numbers]
        _numbers = list(set([n for n in range(1, self.numbers_in_lotto + 1)]) - set(_eons))
        future_game_numbers = None
        current_game_numbers = self.gen_probability.game_objs[0].numbers
        for i in range(3000):
            shuffle(_numbers)
            future_game_numbers = _numbers[0:8]
            if self._comparison_combination_options(future_game_numbers):
                continue
            if self._comparison_current_game(future_game_numbers, current_game_numbers):
                continue
            if self._comparison_exclude_two_numbers(future_game_numbers, self.exclude_two_numbers):
                continue
            if self._comparison_exclude_three_numbers(future_game_numbers, self.exclude_three_numbers):
                continue
            if self._comparison_all_game_numbers(future_game_numbers):
                continue
            break

        return {'numbers': sorted(future_game_numbers), 'add_number': self._future_add_number()}

    def print_info(self, dict_info: dict):
        s = str()
        for k, v in dict_info.items():
            s = s + f'{k}: {v}\n'
        return s

    def add_arguments(self, parser):
        parser.add_argument('name_game', type=str, help='Name game')
        parser.add_argument('--cycle_range', type=int, help='Cycle range all command',)

    def handle(self, *args, **kwargs):
        self.init_before_cycle(*args, **kwargs)

        for _ in range(0, self.cycle_range):
            resp_command = self.get_connects()
            time_now = datetime.now(pytz.timezone('Europe/Moscow'))
            force_sleep, self.sleep_cycle = self.get_sleep_cycle(time_now, resp_command)
            if not force_sleep and self.evaluate_future_game():
                choice_numbers = self.pc_choice_numbers()
                print(self.print_info(self.info_evaluate_future_game['update_one']))
                print(self.print_info(self.info_evaluate_future_game['update_two']))
                print(self.info_evaluate_future_game['reason_for_choice'])
                send_mail(
                    f'choice_numbers: {self.start_game_id + 1}',
                    f'{choice_numbers}\n\n\n{self.print_info(self.info_evaluate_future_game)}',
                    self.EMAIL_HOST_USER,
                    [self.SEND_EMAIL],
                    fail_silently=False,
                )

                self.old_game_id = self.start_game_id

            print(self.old_game_id, 'self.old_game_id')
            self.stdout.write(f"Time before sleep: {time_now}, {self.sleep_cycle}s")
            time.sleep(self.sleep_cycle)
