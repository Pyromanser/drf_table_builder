from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from table_builder.models import DynamicTable, DynamicColumn


class DynamicColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicColumn
        fields = ('pk', 'name', 'table', 'field_type', 'created', 'modified')
        read_only_fields = ('table',)


class DynamicTableSerializer(WritableNestedModelSerializer):
    columns = DynamicColumnSerializer(many=True)

    class Meta:
        model = DynamicTable
        fields = ('pk', 'name', 'columns', 'created', 'modified')
