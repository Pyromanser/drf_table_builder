from rest_framework import serializers
from drf_writable_nested import UniqueFieldsMixin
from drf_writable_nested.serializers import WritableNestedModelSerializer

from table_builder.models import DynamicTable, DynamicColumn


class DynamicColumnSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = DynamicColumn
        fields = ('pk', 'name', 'table', 'field_type', 'created', 'modified')
        read_only_fields = ('table',)


class DynamicTableSerializer(WritableNestedModelSerializer):
    columns = DynamicColumnSerializer(many=True)

    class Meta:
        model = DynamicTable
        fields = ('pk', 'name', 'columns', 'created', 'modified')


class DummySerializer(serializers.Serializer):
    """
    Dummy serializer for placeholder.
    """
    id = serializers.IntegerField(read_only=True)
    char_field = serializers.CharField(max_length=255)
    integer_field = serializers.IntegerField()
    boolean_field = serializers.BooleanField()


def serializer_factory(model):
    """
    Create a serializer class for a given model.
    """
    attrs = {
        'Meta': type('Meta', (object,), {
            'model': model,
            'fields': '__all__',

        }),
    }
    return type(f'{model.__name__}Serializer', (serializers.ModelSerializer,), attrs)
