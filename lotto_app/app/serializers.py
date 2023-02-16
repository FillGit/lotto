from django.contrib.auth.models import Group, User
from rest_framework import serializers

from lotto_app.app.models import Game, LottoTickets, StateNumbers
from lotto_app.app.utils import record_correction_game_numbers
from lotto_app.constants import MAX_NUMBERS_IN_LOTTO


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class GameSerializer(serializers.ModelSerializer):
    def validate_numbers(self, value):
        list_numbers = record_correction_game_numbers(value)
        check = [n for n in list_numbers if n.isnumeric() is False]
        if check:
            raise serializers.ValidationError(f"You don't have a numerical value {check}")
        check = [n for n in list_numbers if len(n) > 2]
        if check:
            raise serializers.ValidationError(
                f"There is a value that has more than 2 characters {check}")
        if len(list_numbers) > 90:
            raise serializers.ValidationError(
                f"You have many more numbers than {MAX_NUMBERS_IN_LOTTO} {list_numbers}")
        if len(list_numbers) != len(set(check)):
            raise serializers.ValidationError(
                f"You have same numbers {list_numbers}")
        return " ".join(list_numbers)

    class Meta:
        model = Game
        fields = ['game', 'numbers']


class StateNumberSerializer(serializers.ModelSerializer):
    game = serializers.CharField(source='game_obj.game', read_only=True, allow_null=True)

    class Meta:
        model = StateNumbers
        fields = ['number', 'state', 'game']


class LottoTicketsSerializer(serializers.ModelSerializer):
    game = serializers.CharField(source='game_obj.game', read_only=True, allow_null=True)

    class Meta:
        model = LottoTickets
        fields = ['game', 'ticket_number', 'first_seven_numbers',
                  'ticket_all_numbers', 'taken_ticket']
