from django.urls import include, path
# from django.urls import re_path as url
from rest_framework.routers import DefaultRouter

from lotto_app.app.views.games import GameViewSet
from lotto_app.app.views.lotto_tickets import LottoTicketsViewSet
from lotto_app.app.views.pc_choice import PcChoiceViewSet
from lotto_app.app.views.research.research_8_add import Research8AddViewSet
from lotto_app.app.views.research.research_90 import Research90ViewSet
from lotto_app.app.views.send_email import CheckSendEmailViewSet
from lotto_app.app.views.state_tickets import StateNumbersViewSet
from lotto_app.app.views.users import GroupViewSet, UserViewSet
from lotto_app.app.views.value_previous_games import ValuePreviousGamesViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

router.register(r'game', GameViewSet, basename='game')

router.register(r'value_previous_games', ValuePreviousGamesViewSet, basename='value_previous_games')

router.register(r'state_numbers', StateNumbersViewSet, basename='state_numbers')

router.register(r'pc_choice', PcChoiceViewSet, basename='pc_choice')

router.register(r'research_90', Research90ViewSet, basename='research_90')

router.register(r'research_8_add', Research8AddViewSet, basename='research_8_add')

router.register(r'lotto_tickets', LottoTicketsViewSet, basename='lotto_tickets')

router.register(r'send_email', CheckSendEmailViewSet, basename='send_email')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r'<str:ng>/', include(router.urls)),
    path(r'<str:ng>/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
