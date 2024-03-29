from copy import deepcopy

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.models import Game
from lotto_app.app.utils import get_game_info, index_9_parts, shuffle_numbers
from lotto_app.app.views.games import GameViewSet
from lotto_app.app.views.research.research import ResearchViewSet


class Research90ViewSet(ResearchViewSet):

    @action(detail=True, url_path='comparison_win_ticket', methods=['get'])
    def comparison_win_ticket(self, request, ng, pk=None):
        main_game_obj = self.get_game_obj()

        main_list_win_numbers = main_game_obj.numbers[:60]
        dict_common_numbers = {}

        for _obj in self.get_queryset():
            if _obj.game_id != pk:
                _comparison_list_win_numbers = _obj.numbers[:60]
                set_common_numbers = set(main_list_win_numbers) & set(_comparison_list_win_numbers)
                dict_common_numbers.update({_obj.game_id: [len(set_common_numbers), sorted(list(set_common_numbers))]})

        resp = {'main_game': pk}
        resp.update(dict(sorted(dict_common_numbers.items(), key=lambda item: item[1], reverse=True)))
        return Response(resp, status=200)

    @staticmethod
    def get_comparison_parts_win_ticket(part_consists_of, order_row,
                                        comparison_games_objs,
                                        main_game_obj=None,
                                        main_combination_win_ticket=None,
                                        main_numbers_in_row=None
                                        ):
        if main_game_obj:
            main_combination_win_ticket = main_game_obj.get_combination_win_ticket(part_consists_of, order_row)
            main_numbers_in_row = []
            for numbers in main_combination_win_ticket['numbers_in_row']:
                main_numbers_in_row.extend(numbers)

        dict_comparisons = {_obj.game_id: [] for _obj in comparison_games_objs}
        for _obj in comparison_games_objs:
            _obj_combination_win_ticket = _obj.get_combination_win_ticket(part_consists_of, order_row)
            _obj_numbers_in_row = []
            for numbers in _obj_combination_win_ticket['numbers_in_row']:
                _obj_numbers_in_row.extend(numbers)
            for part in main_combination_win_ticket['parts']:
                if part in _obj_combination_win_ticket['parts'] and not [
                    number for number in part if number in _obj_numbers_in_row
                ] and not [
                    number for number in part if number in main_numbers_in_row
                ]:
                    dict_comparisons[_obj.game_id].append(part)
        return dict_comparisons

    @action(detail=True, url_path='comparison_parts_win_ticket', methods=['get'])
    def comparison_parts_win_ticket(self, request, ng, pk=None):
        main_game_obj = self.get_game_obj()

        how_comparison_games = int(request.query_params.get('how_comparison_games'))
        part_consists_of = int(request.query_params.get('part_consists_of'))
        order_row = int(request.query_params.get('order_row'))

        comparison_games_objs = self.get_general_game_objs().filter(
            game_id_int__lte=int(pk)-1,
            game_id_int__gte=int(pk)-10-how_comparison_games
        ).order_by('-game_id_int')[0:how_comparison_games]

        dict_comparisons = self.get_comparison_parts_win_ticket(part_consists_of, order_row,
                                                                comparison_games_objs, main_game_obj)

        resp = {'main_game': pk}
        resp.update(dict_comparisons)
        return Response(resp, status=200)

    @action(detail=True, url_path='games_no_numbers', methods=['get'])
    def games_no_numbers(self, request, ng, pk):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        if not game_start:
            return Response({"error": "query_params doesn't game_start"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not how_games:
            return Response({"error": "query_params doesn't how_games"},
                            status=status.HTTP_400_BAD_REQUEST)

        game_objs = self.get_general_game_objs().filter(
            game_id_int__lte=game_start,
            game_id_int__gte=game_start-how_games-5
        ).order_by('-game_id_int')[0:how_games]

        if pk not in [game_obj.game_id for game_obj in game_objs]:
            return Response({"error": f"game_id - {game_start} doesn't have in query"},
                            status=status.HTTP_400_BAD_REQUEST)

        dict_no_numbers = {}
        game_index_9_parts = {}
        for game_obj in game_objs:
            game_id = int(game_obj.game_id)
            total_cost_numbers = GameViewSet.get_several_games_info(ng, game_id-1)['total_cost_numbers']
            game_info = get_game_info(game_obj)
            dict_no_numbers[game_id] = GameViewSet.get_several_games_no_numbers(
                total_cost_numbers, game_info)
            game_index_9_parts[game_id] = index_9_parts(total_cost_numbers,
                                                        dict_no_numbers[game_id].keys())
            dict_no_numbers[game_id]['no_numbers_9_parts'] = game_index_9_parts[game_id]

        dict_no_numbers['all_no_numbers_9_parts'] = {}
        for _game, _index_9_parts in game_index_9_parts.items():
            for part, cost in _index_9_parts.items():
                if part not in dict_no_numbers['all_no_numbers_9_parts']:
                    dict_no_numbers['all_no_numbers_9_parts'][part] = cost
                else:
                    dict_no_numbers['all_no_numbers_9_parts'][part] += cost
            dict_no_numbers['all_no_numbers_9_parts'] = dict(
                sorted(dict_no_numbers['all_no_numbers_9_parts'].items(), key=lambda item: item[1]))
        return Response(dict_no_numbers, status=200)

    def _parts_with_the_most_numbers(self, parts):
        return [part for part, val in parts.items() if val > 7]

    def _all_repeat_parts(self, games_index_9_parts):
        three_and_higher = []
        for _game, _index_9_parts in games_index_9_parts.items():
            if len(_index_9_parts[1]) > 3:
                three_and_higher.append(_index_9_parts[1])
        duplicates = []
        for _l in three_and_higher:
            if _l not in duplicates and len([_m for _m in three_and_higher if set(_l).issubset(set(_m))]) > 1:
                duplicates.append(_l)
        return duplicates

    def _add_cost(self, cost, only_most_numbers):
        if only_most_numbers and cost > 7:
            return cost
        elif only_most_numbers and cost <= 7:
            return 0
        else:
            return cost

    def _get_sum_games_index_9_parts(self, games_index_9_parts, only_most_numbers=None):
        sum_games_index_9_parts = {}
        for _game, _index_9_parts in games_index_9_parts.items():
            for part, cost in _index_9_parts[0].items():
                if part not in sum_games_index_9_parts:
                    sum_games_index_9_parts[part] = self._add_cost(cost, only_most_numbers)
                else:
                    sum_games_index_9_parts[part] += self._add_cost(cost, only_most_numbers)
        return dict(sorted(sum_games_index_9_parts.items(), key=lambda item: item[1]))

    @action(detail=True, url_path='games_9_parts_into_win_ticket', methods=['get'])
    def games_9_parts_into_win_ticket(self, request, ng, pk):
        game_start = int(pk)
        how_games = int(request.query_params.get('how_games', 0))
        only_most_numbers = int(request.query_params.get('only_most_numbers', 0))
        if not game_start:
            return Response({"error": "query_params doesn't game_start"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not how_games:
            return Response({"error": "query_params doesn't how_games"},
                            status=status.HTTP_400_BAD_REQUEST)

        game_objs = self.get_general_game_objs().filter(
            game_id_int__lte=game_start,
            game_id_int__gte=game_start-how_games-5
        ).order_by('-game_id_int')[0:how_games]

        if pk not in [game_obj.game_id for game_obj in game_objs]:
            return Response({"error": f"game_id - {game_start} doesn't have in query"},
                            status=status.HTTP_400_BAD_REQUEST)

        games_index_9_parts = {}
        for game_obj in game_objs:
            game_id = int(game_obj.game_id)
            _index_9_parts = index_9_parts(GameViewSet.get_several_games_info(ng, game_id-1)['total_cost_numbers'],
                                           game_obj.get_win_list(game_obj.last_win_number_ticket))
            games_index_9_parts[game_id] = [_index_9_parts, self._parts_with_the_most_numbers(_index_9_parts)]

        copy_games_index_9_parts = deepcopy(games_index_9_parts)
        games_index_9_parts['sum_games_index_9_parts'] = self._get_sum_games_index_9_parts(copy_games_index_9_parts,
                                                                                           only_most_numbers)
        games_index_9_parts['all_repeat_parts'] = self._all_repeat_parts(copy_games_index_9_parts)
        return Response(games_index_9_parts,
                        status=200)

    @staticmethod
    def get_set_numbers_by_parts(name_game, game_id, parts_by_used, add_numbers):
        set_numbers_by_parts = set()
        several_games_info = GameViewSet.get_several_games_info(name_game, game_id)

        for part in parts_by_used:
            set_numbers_by_parts.update(several_games_info['9_parts_numbers'][part])

        set_numbers_by_parts.update(add_numbers)
        return set_numbers_by_parts

    def _get_count_combination(self, comparison_parts_win_ticket):
        count_combination = 0
        for game_id, parts in comparison_parts_win_ticket.items():
            count_combination += len(parts)
        return count_combination

    @action(detail=True, url_path='future_combination_win_ticket', methods=['get'])
    def future_combination_win_ticket(self, request, ng, pk=None):
        how_comparison_games = int(request.query_params.get('how_comparison_games', 10))
        part_consists_of = int(request.query_params.get('part_consists_of', 5))
        order_row = int(request.query_params.get('order_row', 8))

        parts_by_used = [int(part) for part in request.query_params.get('parts_by_used').replace(' ', '').split(',')]
        add_numbers = [int(num) for num in request.query_params.get('add_numbers').replace(' ', '').split(',')]

        comparison_games_objs = self.get_general_game_objs().filter(
            game_id_int__lte=int(pk)-1,
            game_id_int__gte=int(pk)-10-how_comparison_games
        ).order_by('-game_id_int')[0:how_comparison_games]

        if not [_g for _g in comparison_games_objs if _g.game_id == str(int(pk)-1)]:
            return Response({"error": f"query_params doesn't game_id {int(pk)-1}"},
                            status=status.HTTP_400_BAD_REQUEST)

        set_numbers_by_parts = self.get_set_numbers_by_parts(ng,
                                                             int(pk)-1,
                                                             parts_by_used,
                                                             add_numbers)

        set_exclude_numbers = set()
        if 'exclude_numbers' in request.query_params:
            set_exclude_numbers = set([
                int(part) for part in request.query_params.get('exclude_numbers').replace(' ', '').split(',')
            ])
            set_numbers_by_parts = set_numbers_by_parts - set_exclude_numbers

        comparison_parts_win_ticket = {}
        _win_ticket = {}
        _count_combination = {}
        _l = 61 - len(set_numbers_by_parts)
        for i in range(1000):
            _win_ticket[i] = set(shuffle_numbers(set_numbers_by_parts | set_exclude_numbers)[0:_l]) | set_numbers_by_parts

            comparison_parts_win_ticket[i] = self.get_comparison_parts_win_ticket(
                part_consists_of, order_row,
                comparison_games_objs,
                main_game_obj=None,
                main_combination_win_ticket={'parts':
                                             Game.get_parts_numbers(part_consists_of, _win_ticket[i])},
                main_numbers_in_row=Game.get_numbers_in_row(order_row, _win_ticket[i])
            )

            _count_combination[i] = self._get_count_combination(comparison_parts_win_ticket[i])

            if not _count_combination[i]:
                break

        k = [i for i, count in _count_combination.items() if count == min(_count_combination.values())]
        resp = {'main_game': pk}
        resp['future_combination_win_ticket'] = _win_ticket[k[0]]
        resp['set_numbers_by_parts'] = set_numbers_by_parts
        resp['future_add_numbers'] = _win_ticket[k[0]] - set_numbers_by_parts
        resp.update(comparison_parts_win_ticket[k[0]])
        return Response(resp, status=200)
