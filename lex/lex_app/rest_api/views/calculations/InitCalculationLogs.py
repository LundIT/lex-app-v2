import time

from django.db.models import Max
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from lex.lex_app.logging.CalculationLog import CalculationLog
from lex_app.LexLogger.LexLogger import LexLogLevel, LexLogger

def perform_complex_calculation():
    logger = LexLogger().builder(calculation_log=True, flushing=True)
    # Simulate a complex calculation
    logger.add_heading("Test Calculation started", level=1)

    # Step 1: Data Preparation
    logger.add_heading("Step 1: Data Preparation", 2) \
        .add_paragraph("Preparing input data for the calculation...") \
        .add_code_block("data = prepare_input_data()", "python")

    # Simulate data preparation
    time.sleep(1)

    # Step 2: Calculation Process
    calc_builder = logger.builder(LexLogLevel.INFO, flushing=True)
    calc_builder.add_heading("Step 2: Calculation Process", 2)
    calc_builder.add_paragraph("Performing multi-step calculation:")

    for i in range(1, 4):
        calc_builder.add_paragraph(f"Substep {i}: Processing...") \
            .add_code_block(f"result_{i} = process_step_{i}(data)", "python") \
            .sleep(0.5)  # Simulate processing time

    # Step 3: Results Summary
    logger.builder(LexLogLevel.INFO) \
        .add_heading("Step 3: Results Summary", 2) \
        .add_paragraph("Calculation completed. Here's a summary of the results:") \
        .add_table({
        "Metric": ["Accuracy", "Precision", "Recall"],
        "Value": ["95.5%", "92.3%", "97.1%"]
    }) \
 \
        # Additional Details
    details_builder = logger.builder(LexLogLevel.INFO)
    details_builder.add_heading("Additional Details", 2)
    details_builder.add_paragraph("Detailed breakdown of the calculation steps:") \
        .add_code_block("""
def complex_algorithm(data):
    # Step 1: Normalize data
    normalized_data = normalize(data)

    # Step 2: Apply transformation
    transformed_data = apply_transform(normalized_data)

    # Step 3: Calculate final result
    result = aggregate_results(transformed_data)

    return result
""", "python")

    # Final Status
    logger.add_heading("Calculation Status: Complete", level=2)
    logger.add_paragraph("> All steps executed successfully. Results are ready for further analysis.").log()

class InitCalculationLogs(APIView):
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            calculation_record = request.query_params['calculation_record']
            calculation_id = request.query_params['calculation_id']
            offset = int(request.query_params['offset'])

            queryset_calc = CalculationLog.objects.filter(calculation_record=calculation_record,
                                                          calculationId=calculation_id,
                                                          ).order_by("-timestamp").all()
            logs = [log.to_dict() for log in queryset_calc]

            if offset < len(logs):
                logs = logs[offset:min(offset + 5, len(logs))]
            else:
                logs = []


            return JsonResponse({"logs": list(reversed(logs))})
        except Exception as e:
            print(e)
            return JsonResponse({"logs": ""})
