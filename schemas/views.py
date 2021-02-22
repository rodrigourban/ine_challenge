from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action

from .serializers import (
    TableSerializer,
    TableSchemaSerializer,
)
from .models import Table


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = TableSchemaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)

    def destroy(self, request, pk):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        query_params = request.query_params

        if query_params:
            queryset = Table.objects.filter_by_attr(query_params)
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def get_schema(self, request, pk=None):
        try:
            table = Table.objects.get(pk=1)
            serializer = TableSchemaSerializer(table)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def insert_data(self, request, pk=None):
        try:
            table = Table.objects.get(pk=int(pk))
            Table.objects.insert_data(table.pk, request.data)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response(data=e.args[0], status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
