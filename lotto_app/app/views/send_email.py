from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.config import get_from_config


class CheckSendEmailViewSet(viewsets.ModelViewSet):
    SEND_EMAIL = get_from_config('send_email', 'send_email')
    EMAIL_HOST_USER = get_from_config('send_email', 'email_host_user')

    @action(detail=True, url_path='check_send_email', methods=['get'])
    def check_send_email(self, request, ng, pk):
        _send_email = request.query_params.get('email', self.SEND_EMAIL)
        send_mail(
            'check_send_email',
            f'{ng}, {pk}, {self.EMAIL_HOST_USER}',
            self.EMAIL_HOST_USER,
            [_send_email],
            fail_silently=False,
        )
        return Response([ng, pk, self.EMAIL_HOST_USER, _send_email], status=200)
