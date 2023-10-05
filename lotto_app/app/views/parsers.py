from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lotto_app.app.parsers.choise_parsers import ChoiseParsers
from lotto_app.app.serializers import GameSerializer


class ParserViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer

    @action(detail=False, url_path='parsers', methods=['post'])
    def parsers(self, request, ng):
        print('parsers/')
        name_game = ng
        page = request.data['page']
        class_parser = ChoiseParsers(name_game, page).get_class_parser()
        serializer = self.get_serializer(data=class_parser.parser_response_for_view())
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=False, url_path='parsers_mult_pages', methods=['post'])
    def parsers_mult_pages(self, request, ng):
        print('parsers_mult_pages/')
        name_game = ng
        page_start = request.data['page_start']
        page_end = request.data['page_end']
        list_serializers = []
        for page in range(page_start, page_end+1):
            class_parser = ChoiseParsers(name_game, page).get_class_parser()
            serializer = self.get_serializer(data=class_parser.parser_response_for_view())
            serializer.is_valid(raise_exception=True)
            list_serializers.append(serializer)

        serializer_dataset = []
        for serializer in list_serializers:
            self.perform_create(serializer)
            serializer_dataset.append(serializer.data)

        return Response(serializer_dataset, status=201)

    @action(detail=False, url_path='parser_command', methods=['get'])
    def parser_command(self, request, ng):
        print('parser_command/')
        name_game = f'{ng}_command'
        class_parser = ChoiseParsers(name_game, '').get_class_parser()
        return Response(class_parser.parser_response_for_view(), status=200)
