from lotto_app.app.parsers.parser_8_add_numbers import Parser8AddNumbers
from lotto_app.app.parsers.parser_90_numbers import Parser90Numbers

QUANTITY_TICKETS = 300

MAX_NUMBERS_IN_LOTTO = 90

LOTTO_PARSER = {
    '90_numbers': Parser90Numbers,
    '8_add_numbers': Parser8AddNumbers
}

COMBINATION_OPTIONS_8_ADD = {
    '8': [8],
    '7, 1': [7, 1],
    '6, 1, 1': [6, 1, 1],
    '6, 2': [6, 2],
    '5, 1, 1, 1': [5, 1, 1, 1],
    '5, 2, 1': [5, 2, 1],
    '5, 3': [5, 3],
    '4, 1, 1, 1, 1': [4, 1, 1, 1, 1],
    '4, 2, 1, 1': [4, 2, 1, 1],
    '4, 2, 2': [4, 2, 2],
    '4, 3, 1': [4, 3, 1],
    '4, 4': [4, 4],
    '3, 1, 1, 1, 1, 1': [3, 1, 1, 1, 1, 1],
    '3, 2, 1, 1, 1': [3, 2, 1, 1, 1],
    '3, 2, 2, 1': [3, 2, 2, 1],
    '3, 3, 2': [3, 3, 2],
    '2, 1, 1, 1, 1, 1, 1': [2, 1, 1, 1, 1, 1, 1],
    '2, 2, 1, 1, 1, 1': [2, 2, 1, 1, 1, 1],
    '2, 2, 2, 1, 1': [2, 2, 2, 1, 1],
    '2, 2, 2, 2': [2, 2, 2, 2],
    '1, 1, 1, 1, 1, 1, 1, 1': [1, 1, 1, 1, 1, 1, 1, 1],
}
