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
        many_symbols = [n for n in value if len(str(n)) > 2]
        if many_symbols:
            raise serializers.ValidationError(
                f"There is a value that has more than 2 characters - {many_symbols}")
        if len(value) != len(set(value)):
            dup = {x for x in value if value.count(x) > 1}
            raise serializers.ValidationError(
                f"You have same numbers - {dup}")
        return value

    win_card = serializers.DictField(source='get_win_card', read_only=True)
    win_ticket = serializers.DictField(source='get_win_ticket', read_only=True)

    def to_internal_value(self, data):
        if 'str_numbers' in data and data['str_numbers']:
            list_str_numbers = Game.get_list_str_numbers(data['str_numbers'], True)
            data['numbers'] = [int(num) for num in list_str_numbers]
        if 'auto_win' in data and data['auto_win']:
            dirty_numbers = [num for num in data['str_numbers'].replace(' ', ',').split(',') if num]
            data['last_win_number_card'] = dirty_numbers[1][-2:]
            data['last_win_number_ticket'] = dirty_numbers[2][-2:]
        return super().to_internal_value(data)

    class Meta:
        model = Game
        fields = ['name_game', 'game_id', 'numbers', 'no_numbers', 'win_card', 'win_ticket',
                  'last_win_number_card', 'last_win_number_ticket', 'add_numbers']
        extra_kwargs = {'last_win_number_card': {'write_only': True},
                        'last_win_number_ticket': {'write_only': True}}


class StateNumberSerializer(serializers.ModelSerializer):
    game = serializers.CharField(source='game_obj.game', read_only=True, allow_null=True)

    class Meta:
        model = StateNumbers
        fields = ['number', 'state', 'game']


class LottoTicketsSerializer(serializers.ModelSerializer):
    game_id = serializers.CharField(source='game_obj.game_id', read_only=True, allow_null=True)

    class Meta:
        model = LottoTickets
        fields = ['game_id', 'ticket_id', 'first_seven_numbers',
                  'ticket_numbers', 'taken_ticket']
