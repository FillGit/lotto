from django.urls import include, path
from django.urls import re_path as url
from rest_framework.routers import DefaultRouter

from lotto_app.app.views.games import GameViewSet
from lotto_app.app.views.lotto_tickets import LottoTicketsViewSet
from lotto_app.app.views.pc_choice import PcChoiceViewSet
from lotto_app.app.views.researchs import ResearchViewSet
from lotto_app.app.views.state_tickets import StateNumbersViewSet
from lotto_app.app.views.tickets import TicketViewSet
from lotto_app.app.views.users import GroupViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

router.register(r'game', GameViewSet, basename='game')
router.register(r'state_numbers', StateNumbersViewSet, basename='state_numbers')

router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'pc_choice', PcChoiceViewSet, basename='pc_choice')

router.register(r'research', ResearchViewSet, basename='research')

router.register(r'lotto_tickets', LottoTicketsViewSet, basename='lotto_tickets')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
