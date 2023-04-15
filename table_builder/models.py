from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models, connection
from django_extensions.db.models import TimeStampedModel

from table_builder.apps import TableBuilderConfig
from table_builder.validators import validate_table_name, validate_column_name


class DynamicTable(TimeStampedModel, models.Model):
    name = models.CharField("Table Name", max_length=63, unique=True, validators=[validate_table_name])

    def __str__(self):
        return self.name

    def _create_dynamic_model(self):
        fields = {
            field.name: field._get_field() for field in self.columns.all()
        }
        attrs = {
            '__module__': 'table_builder.models',
            'Meta': type('Meta', (object,), {
                'db_table': self.name,
            }),
            **fields,
        }

        model = type(str(self.name), (models.Model,), attrs)
        return model

    @staticmethod
    def _create_table(_model):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(_model)

    @staticmethod
    def _register_model(_model):
        apps.register_model(TableBuilderConfig.name, _model)

    def is_table_exists(self):
        """
        Function to check if a table exists in the database.
        Returns True if the table exists, False otherwise.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass(%s)", [self.name])
            result = cursor.fetchone()
            return result[0] is not None

    def create_dynamic_model(self):
        if not self.is_table_exists():
            _model = self._create_dynamic_model()
            self._create_table(_model)
            self._register_model(_model)
        else:
            raise ValidationError(f"Table with name {self.name} already exists")

    def update_dynamic_model(self, previous_state):
        if self.is_table_exists():
            new_state = dict(self.columns.values_list('name', 'field_type'))
            columns_to_add = set(new_state.keys()) - set(previous_state.keys())
            columns_to_remove = set(previous_state.keys()) - set(new_state.keys())
            columns_to_update = set()
            for column in set(new_state.keys()) & set(previous_state.keys()):
                if new_state[column] != previous_state[column]:
                    columns_to_update.add(column)
            _model = self._create_dynamic_model()
            self._register_model(_model)
            with connection.schema_editor() as schema_editor:
                # Delete removed columns
                for column in columns_to_remove:
                    old_field = DynamicColumn._get_field_by_type(previous_state[column])
                    old_field.set_attributes_from_name(column)
                    schema_editor.remove_field(_model, old_field)
                # Add new columns
                for column in columns_to_add:
                    field = DynamicColumn._get_field_by_type(new_state[column])
                    field.set_attributes_from_name(column)
                    schema_editor.add_field(_model, field)
                # Update existing columns
                for column in columns_to_update:
                    old_field = DynamicColumn._get_field_by_type(previous_state[column])
                    old_field.set_attributes_from_name(column)
                    field = DynamicColumn._get_field_by_type(new_state[column])
                    field.set_attributes_from_name(column)
                    schema_editor.alter_field(_model, old_field, field, strict=False)
        else:
            raise ValidationError(f"Table with name {self.name} does not exist")

    def delete_dynamic_model(self):
        if self.is_table_exists():
            _model = apps.get_model(TableBuilderConfig.name, self.name)
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(_model)
        else:
            raise ValidationError(f"Table with name {self.name} does not exist")


class DynamicColumn(TimeStampedModel, models.Model):
    class FieldTypes(models.TextChoices):
        CHAR_FIELD = 'Char', 'CharField'
        INTEGER_FIELD = 'Integer', 'IntegerField'
        BOOLEAN_FIELD = 'Boolean', 'BooleanField'

    name = models.CharField("Column name", max_length=59, validators=[validate_column_name])
    table = models.ForeignKey(DynamicTable, verbose_name="Table name", on_delete=models.CASCADE, related_name='columns')
    field_type = models.CharField("Field type", max_length=100, choices=FieldTypes.choices, default=FieldTypes.CHAR_FIELD)

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"

    class Meta:
        unique_together = ('name', 'table')

    def _get_field(self):
        return self._get_field_by_type(self.field_type)

    @staticmethod
    def _get_field_by_type(field_type):
        if field_type == DynamicColumn.FieldTypes.CHAR_FIELD:
            return models.CharField(max_length=255)
        elif field_type == DynamicColumn.FieldTypes.INTEGER_FIELD:
            return models.IntegerField()
        elif field_type == DynamicColumn.FieldTypes.BOOLEAN_FIELD:
            return models.BooleanField()
        else:
            raise NotImplementedError("This field type is not supported.")
