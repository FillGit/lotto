from lotto_app.app.parsers.parser_8_add_numbers import Parser8AddNumbers
from lotto_app.app.parsers.parser_90_numbers import Parser90Numbers

QUANTITY_TICKETS = 300

MAX_NUMBERS_IN_LOTTO = 90

LOTTO_PARSER = {
    '90_numbers': Parser90Numbers,
    '8_add_numbers': Parser8AddNumbers
}
