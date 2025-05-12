import datetime
from decimal import Decimal
from uuid import UUID
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.utils.functional import Promise  # Lazy translation objects
from django.core.files.uploadedfile import InMemoryUploadedFile

def _serialize_payload(data):
    """
    Recursively process the data so it becomes JSON serializable.

    Handles:
      - dictionaries, lists
      - datetime, date, and time objects
      - Decimal and UUID fields
      - Django model instances
      - FieldFile and InMemoryUploadedFile (and similar file-type objects)
      - Lazy translation strings
      - QuerySets and sets
    """
    if isinstance(data, dict):
        return {key: _serialize_payload(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_payload(item) for item in data]
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    elif isinstance(data, datetime.date):
        return data.isoformat()
    elif isinstance(data, datetime.time):
        return data.isoformat()
    elif isinstance(data, Decimal):
        return str(data)  # or float(data) if that fits your needs
    elif isinstance(data, UUID):
        return str(data)
    elif isinstance(data, FieldFile):
        return {'name': data.name, 'url': data.url if hasattr(data, 'url') else None}
    elif isinstance(data, InMemoryUploadedFile):
        # Serialize in-memory files by recording key metadata
        return {
            'name': data.name,
            'size': data.size,
            'content_type': data.content_type
        }
    elif isinstance(data, Model):
        return {'id': data.pk, 'display': str(data)}
    elif isinstance(data, Promise):
        return str(data)
    elif hasattr(data, 'all') and callable(data.all):
        # Possibly a QuerySet or related manager, return a serialized list.
        return [_serialize_payload(item) for item in data.all()]
    elif isinstance(data, set):
        return list(data)
    return data