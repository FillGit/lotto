from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from lotto_app.app import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

router.register(r'game', views.GameModelViewSet, basename='game')
router.register(r'tickets', views.TicketViewSet, basename='tickets')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
