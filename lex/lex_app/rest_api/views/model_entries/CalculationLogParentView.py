# import all missing imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from lex.lex_app.logging.CalculationLog import CalculationLog
from lex.lex_app.rest_api.views.model_entries.serializers.CalculationLogTreeSerializer import CalculationLogTreeSerializer

class CalculationLogParentView(APIView):
    def get(self, request, *args, **kwargs):
        child_id = request.query_params.get('childId')
        if not child_id:
            return Response(
                {'error': 'childId query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            child = CalculationLog.objects.get(id=child_id)
        except CalculationLog.DoesNotExist:
            return Response(
                {'error': 'Child not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        parent = child.parent_calculation_log
        if not parent:
            return Response({'data': None})
        serializer = CalculationLogTreeSerializer(parent)
        return Response({'data': serializer.data})
