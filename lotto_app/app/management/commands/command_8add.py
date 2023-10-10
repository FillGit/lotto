import time
from datetime import datetime, timedelta

import pytz
import requests
from django.core.management.base import BaseCommand
from django.db.models import IntegerField
from django.db.models.functions import Cast

from lotto_app.app.management.command_utils import CombinationOptions8Add, Probabilities8Add, Probabilities8AddOneNumber
from lotto_app.app.models import Game
from lotto_app.app.parsers.choise_parsers import ChoiseParsers
from lotto_app.app.utils import str_to_list_of_int
from lotto_app.config import get_from_config


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
    help = 'Show to make command_8add'

    def init_before_cycle(self, *args, **kwargs):
        self.my_host = get_from_config('lotto_url', 'my_host')
        self.name_game = kwargs['name_game']
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
        self.preferred_added_number = None

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
        if self.expected_print_error_command in resp_command['draft_data']:
            self.stdout.write('Данные загружаются на сайт')
            return True, 120
        time_command = resp_command['time_em']
        time_15 = time_command + timedelta(minutes=15)
        if resp_command['game_id'] == self.old_game_id and (time_now - time_15).total_seconds() > 0:
            return True, 300
        return False, (time_15 - time_now).total_seconds()+120

    def _get_forbidden_circulation(self):
        forbidden_circulation_how_games = int(
            get_from_config('command_8add', 'forbidden_circulation_how_games'))
        combination_options = CombinationOptions8Add(
            self.name_game,
            self.start_game_id,
            forbidden_circulation_how_games)
        game_combinations = combination_options.get_game_combinations()
        game_combinations.update(combination_options.get_sum_combination_options(game_combinations))
        if self.gen_option in game_combinations and game_combinations[self.gen_option] == forbidden_circulation_how_games:
            print('forbidden_circulation')
            return True
        return False

    def _get_exclude_one_numbers(self):
        one_number_factors = get_one_number_factors()
        set_exclude_one_numbers = set()
        previous_id = int(self.gen_probability.game_objs[0].game_id)
        for fs in one_number_factors:
            steps_back_games_previous = fs['steps_back_games_previous']
            steps_back_games_small = fs['steps_back_games_small']
            steps_back_games_big = fs['steps_back_games_big']

            _, set_one_numbers = Probabilities8AddOneNumber().get_probability_one_number(
                self.name_game, previous_id,
                steps_back_games_previous,
                steps_back_games_small,
                steps_back_games_big,
                self.gen_probability
            )
            if set_one_numbers:
                set_exclude_one_numbers.update(set_one_numbers)

        exclude_one_numbers = list(set_exclude_one_numbers)
        print(exclude_one_numbers, 'exclude_one_numbers')
        return exclude_one_numbers

    def _get_exclude_group_numbers(self, part_consists_of, steps_back_games,
                                   limit_overlap, limit_amount_seq):
        exceeding_limit_overlap, _ = self.gen_probability.get_exceeding_limit_overlap(
            self.name_game, self.start_game_id,
            part_consists_of, steps_back_games,
            limit_overlap, self.gen_probability
        )
        return [str_to_list_of_int(seq) for seq in exceeding_limit_overlap] if exceeding_limit_overlap and len(
            exceeding_limit_overlap.keys()) >= limit_amount_seq else []

    def _get_exclude_two_numbers(self):
        steps_back_games = int(
            get_from_config('command_8add', 'two_steps_back_games'))
        limit_overlap = int(
            get_from_config('command_8add', 'two_limit_overlap'))
        limit_amount_seq = int(
            get_from_config('command_8add', 'two_limit_amount_seq'))
        exclude_two_numbers = self._get_exclude_group_numbers(2, steps_back_games, limit_overlap, limit_amount_seq)
        print(exclude_two_numbers, 'exclude_two_numbers')
        return exclude_two_numbers

    def _get_exclude_three_numbers(self):
        steps_back_games = int(
            get_from_config('command_8add', 'three_steps_back_games'))
        limit_overlap = int(
            get_from_config('command_8add', 'three_limit_overlap'))
        limit_amount_seq = int(
            get_from_config('command_8add', 'three_limit_amount_seq'))
        exclude_three_numbers = self._get_exclude_group_numbers(3, steps_back_games, limit_overlap, limit_amount_seq)
        print(exclude_three_numbers, 'exclude_three_numbers')
        return exclude_three_numbers

    def _get_preferred_added_number(self):
        return None

    def evaluate_future_game(self):
        self.start_game_id = int(self._get_start_game_id())
        self.gen_probability = Probabilities8Add(self.name_game,
                                                 self.start_game_id,
                                                 int(get_from_config('command_8add', 'how_games')))
        if self._get_forbidden_circulation():
            self.old_game_id = self.start_game_id
            return False
        i = 0
        self.exclude_one_numbers = self._get_exclude_one_numbers()
        self.exclude_two_numbers = self._get_exclude_two_numbers()
        self.exclude_three_numbers = self._get_exclude_three_numbers()
        self.preferred_added_number = self._get_preferred_added_number()
        i = 0
        if self.exclude_one_numbers:
            i += 1
        if self.exclude_two_numbers:
            i += 1
        if self.exclude_three_numbers:
            i += 1
        if self.preferred_added_number:
            i += 1
        if i >= 2:
            return True
        self.old_game_id = self.start_game_id
        return False

    def pc_choice_numbers(self):
        return False

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
                print('choice_numbers', choice_numbers)
                self.old_game_id = self.start_game_id

            print(self.old_game_id, 'self.old_game_id')
            self.stdout.write(f"Time before sleep: {time_now}, {self.sleep_cycle}s")
            time.sleep(self.sleep_cycle)
