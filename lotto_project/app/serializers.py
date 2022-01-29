from django.contrib.auth.models import User, Group
from rest_framework import serializers
from lotto_project.app.models import Game


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['game', 'numbers',]