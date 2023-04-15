from rest_framework import viewsets

from table_builder.serializers import DynamicTableSerializer

from table_builder.models import DynamicTable


class DynamicTableViewSet(viewsets.ModelViewSet):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer
