from django.urls import include, path
from django.urls import re_path as url
from rest_framework.routers import DefaultRouter

from lotto_app.app import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

router.register(r'game', views.GameViewSet, basename='game')
router.register(r'state_numbers', views.StateNumbersViewSet, basename='state_numbers')

router.register(r'tickets', views.TicketViewSet, basename='tickets')
router.register(r'pc_choice', views.PcChoiceViewSet, basename='pc_choice')

router.register(r'lotto_tickets', views.LottoTicketsViewSet, basename='lotto_tickets')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
