from datetime import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from schemas.models import Table, Attribute
from schemas.serializers import (
    TableSerializer,
    TableSchemaSerializer,
)
from schemas.factories import TableFactory, AttributeFactory


class TableTests(APITestCase):
    """
    # Test table creation success
    # Test table creation fail attrs
    # Test table create with nested table success
    # Test table create with nested table fail attrs
    # Test get table information schema
    # Test soft delete table
    # Test list all tables
    # Test get filtered table
    """

    def test_table_creation_success(self):
        url = reverse('table-list')
        data = {
            'name': 'movies',
            'fields': [
                {
                    'name': 'title',
                    'attr_type': 'str',
                    'unique': True,
                    'required': True
                },
                {
                    'name': 'genre',
                    'attr_type': 'str',
                },
                {
                    'name': 'release_date',
                    'attr_type': 'datetime',
                },
            ]
        }
        expected_response = {
            'name': 'movies',
            'fields': [
                {
                    'name': 'title',
                    'attr_type': 'str',
                    'unique': True,
                    'required': True
                },
                {
                    'name': 'genre',
                    'attr_type': 'str',
                    'unique': False,
                    'required': False
                },
                {
                    'name': 'release_date',
                    'attr_type': 'datetime',
                    'unique': False,
                    'required': False
                },
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Table.objects.count(), 1)
        self.assertEqual(Attribute.objects.count(), 3)
        self.assertEqual(response.data, expected_response)

    def test_table_creation_fail(self):
        url = reverse('table-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Table.objects.count(), 0)

    def test_table_get_one(self):
        dummy_table = TableFactory.create_batch(3)
        dummy_attrs = AttributeFactory.create_batch(
            2,
            table=dummy_table[2],
            attr_type='str',
            value='test value'
        )
        dummy_attrs2 = AttributeFactory.create_batch(
            3,
            table=dummy_table[0]
        )
        expected_result = TableSerializer(dummy_table[2]).data
        url = reverse('table-detail', kwargs={'pk': dummy_table[2].id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_table_list_all(self):
        dummy_tables = TableFactory.create_batch(5)
        url = reverse('table-list')
        data = {}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(dummy_tables), response.data['count'])

    def test_table_list_filtered_tables(self):
        dummy_tables = TableFactory.create_batch(5)
        dummy_attr1 = AttributeFactory(
            table=dummy_tables[0],
            attr_type='str',
            name='title',
            value='Inception')
        dummy_attr2 = AttributeFactory(
            table=dummy_tables[2],
            name='title',
            attr_type='str',
            value='Die Hard')
        dummy_attr3 = AttributeFactory(
            table=dummy_tables[2],
            name='rating',
            attr_type='float',
            value=8.5)
        query_params = f'?title={dummy_attr2.value}'
        url = reverse('table-list') + query_params
        expected_data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [TableSerializer(dummy_tables[2]).data]
        }
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(response.data, expected_data)

    def test_table_delete(self):
        table = TableFactory()
        url = reverse('table-detail', kwargs={'pk': table.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Table.objects.count(), 0)

    def test_table_get_schema(self):
        dummy_table = TableFactory()
        dummy_fields = AttributeFactory.create_batch(
            5,
            table=dummy_table
        )
        url = reverse('table-get-schema', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            TableSchemaSerializer(dummy_table).data
        )


class AttributeTests(APITestCase):
    """
    # Test attribute type retrieve success int be int
    # Test attribute type creation fail 403
    # Test add attribute value to table success
    # Test add attribute value to table fail
    """

    def setUp(self):
        self.dummy_table = TableFactory()
        self.dummy_table2 = TableFactory()
        self.dummy_int_field = AttributeFactory(
            table=self.dummy_table,
            attr_type='int',
        )
        self.dummy_str_field = AttributeFactory(
            table=self.dummy_table,
            attr_type='str',
        )
        self.dummy_bool_field = AttributeFactory(
            table=self.dummy_table,
            attr_type='bool',
        )
        self.dummy_float_field = AttributeFactory(
            table=self.dummy_table,
            attr_type='float',
        )
        self.dummy_datetime_field = AttributeFactory(
            table=self.dummy_table,
            attr_type='datetime',
        )
        self.dummy_required_field = AttributeFactory(
            table=self.dummy_table2,
            attr_type='int',
            required=True
        )

    def test_attribute_set_int_success(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_int_field.name] = 5
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Attribute.objects.get(name=self.dummy_int_field.name).value,
            5)

    def test_attribute_set_int_fail(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_int_field.name] = 'notanumber'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(
            Attribute.objects.get(name=self.dummy_int_field.name).value
        )

    def test_attribute_set_float_success(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_float_field.name] = 5.7
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Attribute.objects.get(name=self.dummy_float_field.name).value,
            5.7)

    def test_attribute_set_float_fail(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_float_field.name] = 'notanumber'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(
            Attribute.objects.get(name=self.dummy_float_field.name).value
        )

    def test_attribute_set_str_success(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_str_field.name] = 'comfortablynumb'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Attribute.objects.get(name=self.dummy_str_field.name).value,
            'comfortablynumb')

    def test_attribute_set_str_fail(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_str_field.name] = 1337
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(
            Attribute.objects.get(name=self.dummy_str_field.name).value
        )

    def test_attribute_set_bool_success(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_bool_field.name] = False
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Attribute.objects.get(name=self.dummy_bool_field.name).value,
            False)

    def test_attribute_set_bool_fail(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_bool_field.name] = 6.6
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(
            Attribute.objects.get(name=self.dummy_bool_field.name).value
        )

    def test_attribute_set_datetime_success(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_datetime_field.name] = '6/6/2006'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Attribute.objects.get(name=self.dummy_datetime_field.name).value,
            datetime.strptime('6/6/2006', '%d/%m/%Y'))

    def test_attribute_set_datetime_fail(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table.id})
        data = {}
        data[self.dummy_datetime_field.name] = 'definitely/not/a/date'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(
            Attribute.objects.get(name=self.dummy_datetime_field.name).value
        )

    def test_attribute_set_all_values_fail_missing_required_attribute(self):
        url = reverse('table-insert-data', kwargs={'pk': self.dummy_table2.id})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(
            Attribute.objects.get(name=self.dummy_required_field.name).value
        )
