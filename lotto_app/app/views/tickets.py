import requests
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lotto_app.app.utils import tickets_from_stoloto, tickets_check_status_code, get_tickets

class TicketViewSet(ViewSet):
    url = 'https://www.stoloto.ru/p/api/mobile/api/v34/games/change?game=ruslotto&count=20'


    def _get_headers(self):
        return {
            'authority': 'www.stoloto.ru',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'isgua=false; gjac=true; K=1642151922907; _gid=GA1.2.1691369319.1642151925; tmr_lvid=a90c18dbe1e0f136a13e2a4f5dfb8a15; tmr_lvidTS=1642151925164; __asc=17b3109a17e57e1d66f38b421f6; __auc=17b3109a17e57e1d66f38b421f6; _ym_uid=1642151926461247036; _ym_d=1642151926; _gcl_au=1.1.641682331.1642151926; welcome=true; _SI_VID_1.6befd9a02400013179aba889=7b02479e5830db4f8bb23b0b; _SI_DID_1.6befd9a02400013179aba889=3d560bdb-5518-3a36-ae5e-9992b2d72181; _ym_visorc=w; _ym_isad=2; mars=4588c92eae9a46878357353bc21ab93a; _fbp=fb.1.1642151930864.265697768; afUserId=cb061fd5-c423-4651-b7cd-ae2b282fcc65-p; AF_SYNC=1642151931693; flocktory-uuid=6f1882c5-4f06-4829-bf5e-fdd9f5d1fd5b-3; _sp_ses.968b=*; allotted-purchase-time-ruslotto=ctrl; dbl=b57a5da72b684be19a60d9e364d3d8eb; semantiqo_sid=9e3c6a1024ea435f866a7c4ff683a845; nbtmmm=%3D0lWyJtb2FuZGNvbUBtYWlsLnJ1I; ga=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJycyI6IjI4MTAwMDAwMDAwMDAiLCJyIjp0cnVlLCJzZWciOjEsImdhYSI6ZmFsc2UsInciOjc1NDMyNDUyMTQ5MywiaSI6MjQ0OTczNjI5NSwiZXhwIjoxNjQyMTUyODMwLCJtIjoiNzkxMzg2MDY2MDIiLCJvIjp0cnVlLCJ1ZCI6MTY0MDkzMjg4ODgwNn0.zXSD06yE4aEG5V-g2GSAwI5-bClhFFjWlOC_1fxNkbo; _ga_W13573SET9=GS1.1.1642151926.1.1.1642152264.0; _ubtcuid=ckye727820000317tyfaj3pwg; _ga=GA1.2.697635581.1642151925; _sp_id.968b=05d2aecb-56b6-403e-a8fb-a9a185219cf1.1642151932.1.1642152268.1642151932.ab062b6a-0fdb-4b39-87bf-b8ebd78d8d9b; tmr_detect=0%7C1642152271106; _SI_SID_1.6befd9a02400013179aba889=a581976c539ffa20f632fc1a.1642152282872.125665; tmr_reqNum=36'
        }

    @action(detail=False, url_path='simple_tickets', methods=['get'])
    def simple_tickets(self, request):
        payload = {'test': 'pass test simple_tickets'}
        return Response(payload, status=200)

    @action(detail=False, url_path='rus_tickets_from_stoloto', methods=['get'])
    def rus_tickets_from_stoloto(self, request):
        response = tickets_from_stoloto(self.url, headers=self._get_headers())
        return Response(response.json(), status=response.status_code)

    @action(detail=False, url_path='rus_dict_tickets', methods=['get'])
    def rus_dict_tickets(self, request):
        response = tickets_from_stoloto(self.url, self._get_headers())
        response_json = tickets_check_status_code(response)
        tickets = get_tickets(response_json)

        return Response(tickets, status=200)
