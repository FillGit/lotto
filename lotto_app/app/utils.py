from random import shuffle


def get_cost_numbers(numbers, mult):
    high_cost = 90
    cost_numbers = {}
    for num in numbers:
        cost_numbers[num] = round(high_cost * mult)
        high_cost = high_cost - 1

    for num in range(1, 91):
        if num not in cost_numbers:
            cost_numbers[num] = 0
    return cost_numbers


def _get_cells():
    cells = {}
    for i in range(0, 9):
        cells[i] = {'nominal_numbers': [],
                    'kit': [num + 10 * i for num in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]}
    cells[8]['kit'].append(90)
    return cells


def _get_nominal(number):
    nominal = 0 if len(number) == 1 else int(number[0])
    if nominal == 9:
        nominal = 8
    return nominal


def get_bingo_30(str_numbers=None, cost_numbers=None, amount=30):
    if str_numbers:
        numbers = [str(n) for n in str_numbers]
    else:
        numbers = [str(n) for n in cost_numbers.keys()]
    cells = _get_cells()
    take_number = []
    for num in numbers:
        nominal = _get_nominal(num)
        num = int(num)
        if len(cells[nominal]['nominal_numbers']) < 3 and num in cells[nominal]['kit']:
            cells[nominal]['nominal_numbers'].append(num)
            take_number.append(num)
        if len(take_number) == 27:
            break

    if amount <= 27:
        return sorted(take_number[0:amount])

    for num in numbers:
        nominal = _get_nominal(num)
        num = int(num)
        if num not in take_number and len(cells[nominal]['nominal_numbers']) < 4 \
                and num in cells[nominal]['kit']:
            cells[nominal]['nominal_numbers'].append(num)
            take_number.append(num)
        if len(take_number) == 30:
            break

    return sorted(take_number)


def index_bingo(cost_numbers, bingo):
    sum = 0
    for num in bingo:
        sum = sum + cost_numbers[int(num)]
    return sum


def index_9_parts(cost_numbers, bingo):
    sum_9_parts = {}
    _9_parts = {n: [v, None] for n, v in cost_numbers.items()}

    i = 0
    for num, v in _9_parts.items():
        _9_parts[num][1] = _get_nominal(str(i))
        i += 1

    for num in bingo:
        nominal = _9_parts[num][1]
        if nominal not in sum_9_parts:
            sum_9_parts[nominal] = 0
        sum_9_parts[nominal] += 1

    return dict(sorted(sum_9_parts.items(), key=lambda x: x[0]))


def get_9_parts_numbers(sorted_cost_numbers):
    _9_parts_numbers = {}
    for i in range(0, 9):
        _9_parts_numbers[i] = list(sorted_cost_numbers.keys())[i*10: i*10+10]
    return _9_parts_numbers


def get_game_info(game_obj, mult=None):
    if not mult:
        mult = 1
    numbers = game_obj.numbers
    cost_numbers = get_cost_numbers(numbers, mult)

    return {'cost_numbers': cost_numbers,
            'bingo_30': get_bingo_30(numbers)
            }


def get_str_numbers(list_numbers):
    return ' '.join(map(str, list_numbers))


def shuffle_numbers(set_exist_numbers=None, numbers_in_lotto=90):
    if set_exist_numbers:
        minus_numbers = [mn for mn in range(1, numbers_in_lotto+1) if mn not in set_exist_numbers]
    else:
        minus_numbers = [mn for mn in range(1, numbers_in_lotto+1)]
    shuffle(minus_numbers)
    return minus_numbers


def sort_numbers(list_items, min, max, reverse=False, _dict=False):
    _count_numbers = {n: list_items.count(n) for n in range(min, max+1)}
    if _dict:
        return dict(sorted(_count_numbers.items(), key=lambda x: x[1], reverse=reverse))

    return [n for n in dict(sorted(_count_numbers.items(), key=lambda x: x[1], reverse=reverse))]
