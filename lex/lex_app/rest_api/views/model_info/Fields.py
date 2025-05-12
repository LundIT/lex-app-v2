from django.db.models import (
    ForeignKey,
    IntegerField,
    FloatField,
    BooleanField,
    DateField,
    DateTimeField,
    FileField,
    ImageField,
    AutoField,
    JSONField,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from lex.lex_app.rest_api.fields.Bokeh_field import BokehField
from lex.lex_app.rest_api.fields.HTML_field import HTMLField
from lex.lex_app.rest_api.fields.PDF_field import PDFField
from lex.lex_app.rest_api.fields.XLSX_field import XLSXField
from lex.lex_app.rest_api.views.permissions.UserPermission import UserPermission

# Import CalculationLog so we can check for it and add the extra virtual field.
from lex.lex_app.logging.CalculationLog import CalculationLog

DJANGO_FIELD2TYPE_NAME = {
    ForeignKey: "foreign_key",
    IntegerField: "int",
    FloatField: "float",
    BooleanField: "boolean",
    DateField: "date",
    DateTimeField: "date_time",
    FileField: "file",
    PDFField: "pdf_file",
    XLSXField: "xlsx_file",
    HTMLField: "html",
    BokehField: "bokeh",
    ImageField: "image_file",
    JSONField: "json",
}

DEFAULT_TYPE_NAME = "string"


def create_field_info(field):
    default_value = None
    # Use field.get_default() only if a default is set
    if field.get_default() is not None:
        default_value = field.get_default()

    field_type = type(field)
    additional_info = {}
    if field_type == ForeignKey:
        additional_info["target"] = field.target_field.model._meta.model_name

    return {
        "name": field.name,
        "readable_name": field.verbose_name.title(),
        "type": DJANGO_FIELD2TYPE_NAME.get(field_type, DEFAULT_TYPE_NAME),
        # AutoFields normally should not be edited
        "editable": field.editable and not field_type == AutoField,
        "required": not (field.null or default_value),
        "default_value": default_value,
        **additional_info,
    }


class Fields(APIView):
    http_method_names = ["get"]
    permission_classes = [HasAPIKey | IsAuthenticated, UserPermission]

    def get(self, *args, **kwargs):
        # Retrieve the model class from the model_container.
        model = kwargs["model_container"].model_class
        # Get all concrete fields defined via _meta.fields.
        concrete_fields = model._meta.fields

        # Build field info for concrete fields.
        fields_info = [create_field_info(field) for field in concrete_fields]

        # If the model is CalculationLog (or a subclass), remove unwanted fields and add a virtual field.
        if issubclass(model, CalculationLog):
            # Remove the fields 'content_type' and 'object_id'
            fields_info = [
                f for f in fields_info if f["name"] not in ["content_type", "object_id"]
            ]

            # Add the virtual GenericForeignKey field "calculatable_object"
            virtual_field = {
                "name": "calculation_record",
                "readable_name": "Calculation Record",
                "type": "string",  # You can use a custom type if needed
                "editable": False,  # Typically not editable directly
                "required": False,
                "default_value": None,
            }
            fields_info.append(virtual_field)

        field_info = {"fields": fields_info, "id_field": model._meta.pk.name}
        # Optionally, send additional arrays for table view fields if needed.
        return Response(field_info)
