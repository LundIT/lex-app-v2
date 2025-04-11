from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from lex.lex_app.logging.CalculationLog import CalculationLog  # Import your CalculationLog model
from lex.lex_app.rest_api.views.permissions.UserPermission import UserPermission

# --- CalculationLog Serializer ---
class CalculationLogSerializer(serializers.ModelSerializer):
    # Changed the field name to "calculated_status"
    calculation = serializers.SerializerMethodField()

    class Meta:
        model = CalculationLog
        fields = [
            'calculationId',
            'id',
            'calculation_record',
            'message',
            'timestamp',
            'trigger_name',
            'calculation',  # renamed field now appears in the output
            'method',
            'is_notification',
            'message_type',
            'detailed_message',
            'auditlog',
            'calculationlog'
        ]

    def get_calculation(self, obj):
        """
        Return a JSON-serializable representation (for example, a flag) derived from the generically related object.
        In this case, we're using a property named 'is_calculated' from the linked object.
        """
        if obj.content_type and obj.object_id:
            return str(obj.calculatable_object)
            # return obj.calculatable_object.is_calculated
        return None

# --- ModelEntryProviderMixin ---
class ModelEntryProviderMixin:
    permission_classes = [HasAPIKey | IsAuthenticated, UserPermission]

    def get_queryset(self):
        return self.kwargs['model_container'].model_class.objects.all()

    def get_serializer_class(self):
        model_class = self.kwargs['model_container'].model_class
        # If the model is CalculationLog (or a subclass thereof) use the CalculationLogSerializer.
        if issubclass(model_class, CalculationLog):
            return CalculationLogSerializer
        else:
            return self.kwargs['model_container'].obj_serializer
