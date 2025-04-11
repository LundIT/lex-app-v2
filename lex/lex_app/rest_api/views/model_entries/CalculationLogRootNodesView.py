# import all missing imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from lex.lex_app.logging.CalculationLog import CalculationLog
from lex.lex_app.rest_api.views.model_entries.serializers.CalculationLogTreeSerializer import CalculationLogTreeSerializer

class CalculationLogRootNodesView(APIView):
    def get(self, request, *args, **kwargs):
        calculation_id = request.query_params.get('calculation_id')
        if calculation_id:
            roots = CalculationLog.objects.filter(
                calculationId=calculation_id,
                parent_calculation_log__isnull=True
            )
        else:
            roots = CalculationLog.objects.filter(parent_calculation_log__isnull=True)
        serializer = CalculationLogTreeSerializer(roots, many=True)
        return Response({'data': serializer.data})