# import all missing imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from lex.lex_app.logging.CalculationLog import CalculationLog
from lex.lex_app.rest_api.views.model_entries.serializers.CalculationLogTreeSerializer import CalculationLogTreeSerializer

class CalculationLogChildrenView(APIView):
    def get(self, request, *args, **kwargs):
        parent_id = request.query_params.get('parentId')
        if not parent_id:
            return Response(
                {'error': 'parentId query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            parent = CalculationLog.objects.get(id=parent_id)
        except CalculationLog.DoesNotExist:
            return Response(
                {'error': 'Parent not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Retrieve children belonging to the same calculation.
        children = CalculationLog.objects.filter(
            parent_calculation_log=parent,
            calculationId=parent.calculationId
        )
        serializer = CalculationLogTreeSerializer(children, many=True)
        return Response({'data': serializer.data})
