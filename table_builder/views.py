from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from table_builder.serializers import DynamicTableSerializer, DummySerializer, serializer_factory

from table_builder.models import DynamicTable


class DynamicTableViewSet(viewsets.ModelViewSet):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer
    http_method_names = ["get", "post", "put", "delete", "head", "options", "trace"]

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.create_dynamic_model()

    def perform_update(self, serializer):
        previous_state = dict(DynamicTable.objects.get(pk=self.get_object().pk).columns.values_list('name', 'field_type'))
        obj = serializer.save()
        obj.update_dynamic_model(previous_state)

    def perform_destroy(self, instance):
        instance.delete_dynamic_model()
        instance.delete()

    @action(detail=True, methods=['post'], serializer_class=DummySerializer)
    def row(self, request, pk=None):
        dynamic_model = self.get_object().get_dynamic_model()
        serializer = serializer_factory(dynamic_model)(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        responses={
            200: DummySerializer(many=True),
        }
    )
    @action(detail=True, methods=['get'], serializer_class=DummySerializer)
    def rows(self, request, pk=None):
        dynamic_model = self.get_object().get_dynamic_model()
        serializer = serializer_factory(dynamic_model)(dynamic_model.objects.all(), many=True)
        return Response(serializer.data)
