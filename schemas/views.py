from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action

from .serializers import (
    TableSerializer,
    TableSchemaSerializer,
)
from .models import Table


class TableViewSet(viewsets.ModelViewSet):
    """
    This viewset represents the CRUD and extra actions for SQL Simulation
    """
    queryset = Table.objects.all()
    serializer_class = TableSchemaSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        Creates a new table with attributes
        """
        serializer = TableSchemaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)

    def destroy(self, request, pk):
        """
        Deletes a table an all it's attributes
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        List and filter tables, queryparams are allowed
        """
        query_params = request.query_params

        if query_params:
            queryset = Table.objects.filter_by_attr(query_params)
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TableSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TableSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves one table by id
        """
        instance = self.get_object()
        serializer = TableSerializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_schema(self, request, pk=None):
        """
        Retrieves table's schema by id
        """
        try:
            table = Table.objects.get(pk=1)
            serializer = TableSchemaSerializer(table)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def insert_data(self, request, pk=None):
        """
        Inserts data into the attributes of an existing table
        """
        try:
            table = Table.objects.get(pk=int(pk))
            Table.objects.insert_data(table.pk, request.data)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response(data=e.args[0], status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
