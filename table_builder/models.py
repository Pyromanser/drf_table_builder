from django.db import models
from django_extensions.db.models import TimeStampedModel


class DynamicTable(TimeStampedModel, models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DynamicColumn(TimeStampedModel, models.Model):
    CHAR_FIELD = 'Char'
    INTEGER_FIELD = 'Integer'
    BOOLEAN_FIELD = 'Boolean'
    FIELD_TYPES_CHOICES = (
        (CHAR_FIELD, 'CharField'),
        (INTEGER_FIELD, 'IntegerField'),
        (BOOLEAN_FIELD, 'BooleanField'),
    )

    name = models.CharField(max_length=100)
    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name='columns')
    field_type = models.CharField(max_length=100, choices=FIELD_TYPES_CHOICES, default=CHAR_FIELD)

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"

    class Meta:
        unique_together = ('name', 'table')
