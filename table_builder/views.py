from rest_framework import viewsets

from table_builder.serializers import DynamicTableSerializer

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
