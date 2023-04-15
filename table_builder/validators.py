import re

from django.core.exceptions import ValidationError


def validate_table_name(value):
    """
    Custom validator to ensure that the field value is a valid table name.
    """
    # Define the regex pattern for valid table names
    pattern = r'^[a-z][a-z0-9_]*$'
    restricted_names = ['django_admin_log', 'django_content_type', 'django_migrations', 'django_session']

    # Check if the value matches the regex pattern
    if not re.match(pattern, value):
        raise ValidationError(
            'Table name can only contain letters, numbers, and underscores, and must start with a letter.'
        )
    for name in restricted_names:
        if value == name:
            raise ValidationError(
                'Table name cannot be a reserved word.'
            )


def validate_column_name(value):
    """
    Custom validator to ensure that the field value is a valid column name.
    """
    # Define the regex pattern for valid column names
    pattern = r'^[a-z][a-z0-9_]*$'
    restricted_names = ['id']

    # Check if the value matches the regex pattern
    if not re.match(pattern, value):
        raise ValidationError(
            'Column name can only contain letters, numbers, and underscores, and must start with a letter.'
        )
    for name in restricted_names:
        if value == name:
            raise ValidationError(
                'Column name cannot be a reserved word.'
            )
