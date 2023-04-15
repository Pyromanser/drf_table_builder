from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient

from table_builder.models import DynamicTable, DynamicColumn
from table_builder.serializers import DynamicTableSerializer


class PublicDynamicTableApiTests(TestCase):
    """Test the publicly available DynamicTable API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_not_required(self):
        """Test that login is required for retrieving DynamicTable"""
        res = self.client.get(reverse_lazy('table_builder:table-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_required(self):
        """Test that login is required for retrieving DynamicTable"""
        res = self.client.post(reverse_lazy('table_builder:table-list'))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDynamicTableApiTests(TestCase):
    """Test the authorized user DynamicTable API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test',
            'test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        test_table = DynamicTable.objects.create(
            name='test_table_1',
        )
        DynamicColumn.objects.create(
            name='test_column_char',
            field_type=DynamicColumn.FieldTypes.CHAR_FIELD,
            table=test_table,
        )
        DynamicColumn.objects.create(
            name='test_column_int',
            field_type=DynamicColumn.FieldTypes.INTEGER_FIELD,
            table=test_table,
        )
        DynamicColumn.objects.create(
            name='test_column_bool',
            field_type=DynamicColumn.FieldTypes.BOOLEAN_FIELD,
            table=test_table,
        )
        self.test_table = test_table

    def test_retrieve_tables(self):
        """Test retrieving DynamicTable"""

        res = self.client.get(reverse_lazy('table_builder:table-list'))

        tables = DynamicTable.objects.all().order_by('-name')
        serializer = DynamicTableSerializer(tables, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class DynamicTableRowCreateApiTests(TestCase):
    """Test the creation DynamicTable row by API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test',
            'test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_table(self):
        """Test creating a new DynamicTable"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'name': 'test_column_int',
                    'field_type': DynamicColumn.FieldTypes.INTEGER_FIELD,
                },
                {
                    'name': 'test_column_bool',
                    'field_type': DynamicColumn.FieldTypes.BOOLEAN_FIELD,
                },
            ],
        }
        res = self.client.post(reverse_lazy('table_builder:table-list'), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 3)

    def test_create_table_with_wrong_field_type(self):
        """Test creating a new DynamicTable with wrong field_type"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'name': 'test_column_char',
                    'field_type': 'wrong_field_type',
                },
            ],
        }
        res = self.client.post(reverse_lazy('table_builder:table-list'), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DynamicTable.objects.count(), 0)
        self.assertEqual(DynamicColumn.objects.count(), 0)

    def test_create_table_with_wrong_field_name(self):
        """Test creating a new DynamicTable with wrong field_name"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'name': '1TEST-column```',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
            ],
        }
        res = self.client.post(reverse_lazy('table_builder:table-list'), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DynamicTable.objects.count(), 0)
        self.assertEqual(DynamicColumn.objects.count(), 0)

    def test_create_table_with_wrong_name(self):
        """Test creating a new DynamicTable with wrong name"""
        payload = {
            'name': '1TEST-table```',
            'columns': [
                {
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
            ],
        }
        res = self.client.post(reverse_lazy('table_builder:table-list'), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DynamicTable.objects.count(), 0)
        self.assertEqual(DynamicColumn.objects.count(), 0)


class DynamicTableRowUpdateApiTests(TestCase):
    """Test updating DynamicTable row by API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test',
            'test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.test_table = DynamicTable.objects.create(
            name='test_table_1',
        )
        self.test_column_char = DynamicColumn.objects.create(
            name='test_column_char',
            field_type=DynamicColumn.FieldTypes.CHAR_FIELD,
            table=self.test_table,
        )
        self.test_column_int = DynamicColumn.objects.create(
            name='test_column_int',
            field_type=DynamicColumn.FieldTypes.INTEGER_FIELD,
            table=self.test_table,
        )
        self.test_column_bool = DynamicColumn.objects.create(
            name='test_column_bool',
            field_type=DynamicColumn.FieldTypes.BOOLEAN_FIELD,
            table=self.test_table,
        )
        self.test_table.create_dynamic_model()

    def test_update_without_change_table(self):
        """Test updating a DynamicTable"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'pk': self.test_column_char.pk,
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'pk': self.test_column_int.pk,
                    'name': 'test_column_int',
                    'field_type': DynamicColumn.FieldTypes.INTEGER_FIELD,
                },
                {
                    'pk': self.test_column_bool.pk,
                    'name': 'test_column_bool',
                    'field_type': DynamicColumn.FieldTypes.BOOLEAN_FIELD,
                },
            ],
        }
        res = self.client.put(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 3)

    def test_update_table_with_wrong_field_type(self):
        """Test updating a DynamicTable with wrong field_type"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'pk': self.test_column_char.pk,
                    'name': 'test_column_char',
                    'field_type': 'wrong_field_type',
                },
            ],
        }
        res = self.client.put(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 3)

    def test_update_with_change_table_add_only(self):
        """Test updating a DynamicTable"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'pk': self.test_column_char.pk,
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'pk': self.test_column_int.pk,
                    'name': 'test_column_int',
                    'field_type': DynamicColumn.FieldTypes.INTEGER_FIELD,
                },
                {
                    'pk': self.test_column_bool.pk,
                    'name': 'test_column_bool',
                    'field_type': DynamicColumn.FieldTypes.BOOLEAN_FIELD,
                },
                {
                    'name': 'new_field',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
            ],
        }
        res = self.client.put(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 4)

    def test_update_with_change_table_remove_only(self):
        """Test updating a DynamicTable"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'pk': self.test_column_char.pk,
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'pk': self.test_column_int.pk,
                    'name': 'test_column_int',
                    'field_type': DynamicColumn.FieldTypes.INTEGER_FIELD,
                },
            ],
        }
        res = self.client.put(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 2)

    def test_update_with_change_table_change_only(self):
        """Test updating a DynamicTable"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'pk': self.test_column_char.pk,
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'pk': self.test_column_int.pk,
                    'name': 'test_column_int',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'pk': self.test_column_bool.pk,
                    'name': 'test_column_bool',
                    'field_type': DynamicColumn.FieldTypes.BOOLEAN_FIELD,
                },
            ],
        }
        res = self.client.put(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 3)
        self.assertEqual(DynamicColumn.objects.get(pk=self.test_column_int.pk).field_type, DynamicColumn.FieldTypes.CHAR_FIELD)

    def test_update_with_change_table_combination(self):
        """Test updating a DynamicTable"""
        payload = {
            'name': 'test_table_1',
            'columns': [
                {
                    'pk': self.test_column_char.pk,
                    'name': 'test_column_char',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'pk': self.test_column_int.pk,
                    'name': 'test_column_int',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
                {
                    'name': 'new_field',
                    'field_type': DynamicColumn.FieldTypes.CHAR_FIELD,
                },
            ],
        }
        res = self.client.put(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicColumn.objects.count(), 3)
        self.assertEqual(DynamicColumn.objects.get(pk=self.test_column_int.pk).field_type, DynamicColumn.FieldTypes.CHAR_FIELD)


class DynamicTableRowDeleteApiTests(TestCase):
    """Test updating DynamicTable row by API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test',
            'test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.test_table = DynamicTable.objects.create(
            name='test_table_1',
        )
        self.test_column_char = DynamicColumn.objects.create(
            name='test_column_char',
            field_type=DynamicColumn.FieldTypes.CHAR_FIELD,
            table=self.test_table,
        )
        self.test_column_int = DynamicColumn.objects.create(
            name='test_column_int',
            field_type=DynamicColumn.FieldTypes.INTEGER_FIELD,
            table=self.test_table,
        )
        self.test_column_bool = DynamicColumn.objects.create(
            name='test_column_bool',
            field_type=DynamicColumn.FieldTypes.BOOLEAN_FIELD,
            table=self.test_table,
        )
        self.test_table.create_dynamic_model()

    def test_delete_table(self):
        """Test deleting a DynamicTable"""
        res = self.client.delete(
            reverse_lazy('table_builder:table-detail', kwargs={'pk': self.test_table.pk}),
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DynamicTable.objects.count(), 0)
        self.assertEqual(DynamicColumn.objects.count(), 0)


class DynamicTableRowDataListApiTests(TestCase):
    """Test updating DynamicTable row by API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test',
            'test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.test_table = DynamicTable.objects.create(
            name='test_table_1',
        )
        self.test_column_char = DynamicColumn.objects.create(
            name='test_column_char',
            field_type=DynamicColumn.FieldTypes.CHAR_FIELD,
            table=self.test_table,
        )
        self.test_column_int = DynamicColumn.objects.create(
            name='test_column_int',
            field_type=DynamicColumn.FieldTypes.INTEGER_FIELD,
            table=self.test_table,
        )
        self.test_column_bool = DynamicColumn.objects.create(
            name='test_column_bool',
            field_type=DynamicColumn.FieldTypes.BOOLEAN_FIELD,
            table=self.test_table,
        )
        self.test_table.create_dynamic_model()
        self.test_table.get_dynamic_model().objects.create(
            test_column_char='test',
            test_column_int=1,
            test_column_bool=True,
        )
        self.test_table.get_dynamic_model().objects.create(
            test_column_char='test2',
            test_column_int=2,
            test_column_bool=False,
        )

    def test_get_rows(self):
        """Test getting row data from a DynamicTable"""
        res = self.client.get(
            reverse_lazy('table_builder:table-rows', kwargs={'pk': self.test_table.pk}),
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class DynamicTableRowDataAddApiTests(TestCase):
    """Test updating DynamicTable row by API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test',
            'test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.test_table = DynamicTable.objects.create(
            name='test_table_1',
        )
        self.test_column_char = DynamicColumn.objects.create(
            name='test_column_char',
            field_type=DynamicColumn.FieldTypes.CHAR_FIELD,
            table=self.test_table,
        )
        self.test_column_int = DynamicColumn.objects.create(
            name='test_column_int',
            field_type=DynamicColumn.FieldTypes.INTEGER_FIELD,
            table=self.test_table,
        )
        self.test_column_bool = DynamicColumn.objects.create(
            name='test_column_bool',
            field_type=DynamicColumn.FieldTypes.BOOLEAN_FIELD,
            table=self.test_table,
        )
        self.test_table.create_dynamic_model()

    def test_add_row(self):
        """Test adding a row to a DynamicTable"""
        payload = {
            'test_column_char': 'test',
            'test_column_int': 1,
            'test_column_bool': True,
        }
        res = self.client.post(
            reverse_lazy('table_builder:table-row', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.test_table.get_dynamic_model().objects.count(), 1)
        self.assertEqual(self.test_table.get_dynamic_model().objects.get().test_column_char, 'test')
        self.assertEqual(self.test_table.get_dynamic_model().objects.get().test_column_int, 1)
        self.assertEqual(self.test_table.get_dynamic_model().objects.get().test_column_bool, True)

    def test_add_row_with_missing_field(self):
        """Test adding a row to a DynamicTable with missing field"""
        payload = {
            'test_column_char': 'test',
            'test_column_int': 1,
        }
        res = self.client.post(
            reverse_lazy('table_builder:table-row', kwargs={'pk': self.test_table.pk}),
            payload,
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.test_table.get_dynamic_model().objects.count(), 0)

    def test_add_multiple_rows(self):
        """Test adding multiple rows to a DynamicTable"""
        payload = [
            {
                'test_column_char': 'test',
                'test_column_int': 1,
                'test_column_bool': True,
            },
            {
                'test_column_char': 'test2',
                'test_column_int': 2,
                'test_column_bool': False,
            },
        ]
        res = self.client.post(
            reverse_lazy('table_builder:table-row', kwargs={'pk': self.test_table.pk}),
            payload[0],
            format='json',
        )
        res = self.client.post(
            reverse_lazy('table_builder:table-row', kwargs={'pk': self.test_table.pk}),
            payload[1],
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.test_table.get_dynamic_model().objects.count(), 2)
        self.assertEqual(self.test_table.get_dynamic_model().objects.get(pk=1).test_column_char, 'test')
        self.assertEqual(self.test_table.get_dynamic_model().objects.get(pk=1).test_column_int, 1)
        self.assertEqual(self.test_table.get_dynamic_model().objects.get(pk=1).test_column_bool, True)
        self.assertEqual(self.test_table.get_dynamic_model().objects.get(pk=2).test_column_char, 'test2')
        self.assertEqual(self.test_table.get_dynamic_model().objects.get(pk=2).test_column_int, 2)
        self.assertEqual(self.test_table.get_dynamic_model().objects.get(pk=2).test_column_bool, False)
