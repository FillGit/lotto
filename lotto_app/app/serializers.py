from django.contrib.auth.models import Group, User
from rest_framework import serializers

from lotto_app.app.models import Game, LottoTickets, StateNumbers
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
    def _validate_win_number_more(self, value, limit, name):
        if value > limit:
            raise serializers.ValidationError(
                f"{name} more number than {limit} - {value}")
        return value

    def validate_last_win_number_card(self, value):
        return self._validate_win_number_more(value, MAX_NUMBERS_IN_LOTTO, 'last_win_number_card')

    def validate_last_win_number_ticket(self, value):
        return self._validate_win_number_more(value, MAX_NUMBERS_IN_LOTTO, 'last_win_number_ticket')

    def validate_numbers(self, value):
        _val = value.replace(' ', '')
        list_numbers = Game.record_correction_numbers(
            " ".join([_val[i:i+2] for i in range(0, len(_val), 2)])
            )
        not_numeric = [n for n in list_numbers if n.isnumeric() is False]
        if not_numeric:
            raise serializers.ValidationError(
                f"You don't have a numerical value - {not_numeric}")
        many_symbols = [n for n in list_numbers if len(n) > 2]
        if many_symbols:
            raise serializers.ValidationError(
                f"There is a value that has more than 2 characters - {many_symbols}")
        if len(list_numbers) > MAX_NUMBERS_IN_LOTTO:
            raise serializers.ValidationError(
                f"You have many more numbers than {MAX_NUMBERS_IN_LOTTO} - {len(list_numbers)}")
        if len(list_numbers) != len(set(list_numbers)):
            raise serializers.ValidationError(
                f"You have same numbers - {list_numbers}")
        return " ".join(list_numbers)

    win_card = serializers.DictField(source='get_win_card', read_only=True)
    win_ticket = serializers.DictField(source='get_win_ticket', read_only=True)

    class Meta:
        model = Game
        fields = ['game', 'numbers', 'no_numbers', 'win_card', 'win_ticket', 'last_win_number_card',
                  'last_win_number_ticket']
        extra_kwargs = {'last_win_number_card': {'write_only': True},
                        'last_win_number_ticket': {'write_only': True}}


class StateNumberSerializer(serializers.ModelSerializer):
    game = serializers.CharField(source='game_obj.game', read_only=True, allow_null=True)

    class Meta:
        model = StateNumbers
        fields = ['number', 'state', 'game']


class LottoTicketsSerializer(serializers.ModelSerializer):
    game = serializers.CharField(source='game_obj.game', read_only=True, allow_null=True)

    class Meta:
        model = LottoTickets
        fields = ['game', 'ticket_id', 'first_seven_numbers',
                  'ticket_numbers', 'taken_ticket']
