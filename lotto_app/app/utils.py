import requests

from rest_framework.response import Response

def tickets_from_stoloto(url, headers):
    return requests.get(url, headers=headers)


def tickets_check_status_code(response):
    if response.status_code != 200:
        raise ValueError(f'{response.status_code} and {response.json()}')
    return response.json()


def get_tickets(response_json):
    tickets = {t['barCode']: {'numbers': t['numbers']} for t in response_json['tickets']}
    for key, value in tickets.items():
        value['line_1_1'] = value['numbers'][0:5]
        value['line_1_2'] = value['numbers'][5:10]
        value['line_1_3'] = value['numbers'][10:15]
        value['line_2_1'] = value['numbers'][15:20]
        value['line_2_2'] = value['numbers'][20:25]
        value['line_2_3'] = value['numbers'][25:30]
        value['card_1'] = value['numbers'][0:15]
        value['card_2'] = value['numbers'][15:30]
    print(tickets)
    return tickets