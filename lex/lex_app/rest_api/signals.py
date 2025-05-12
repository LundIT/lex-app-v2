from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from lex.lex_app.lex_models.UpdateModel import UpdateModel

from lex.lex_app.rest_api.calculated_model_updates.update_handler import (
    CalculatedModelUpdateHandler,
)


@receiver(post_save)
def calculation_ids(sender, instance, created, **kwargs):
    from lex.lex_app.logging.CalculationIDs import CalculationIDs

    if sender == CalculationIDs:
        channel_layer = get_channel_layer()

        calculation_record = instance.calculation_record
        calculation_id = instance.calculation_id
        context_id = instance.context_id

        message = {
            "type": "calculation_id",
            "payload": {
                "calculation_record": calculation_record,
                "calculation_id": calculation_id,
                "context_id": context_id,
            },
        }
        async_to_sync(channel_layer.group_send)("calculations", message)


# @receiver(post_save)
# def calculation_logs(sender, instance, created, **kwargs):
#     from lex.lex_app.logging.CalculationLog import CalculationLog
#     from lex.lex_app.logging.UserChangeLog import UserChangeLog
#
#     if sender == CalculationLog:
#         channel_layer = get_channel_layer()
#         message = {
#             'type': 'calculation_log_real_time', # This is the correct naming convention
#             'payload': get_model_data(instance.calculation_record, instance.calculationId)
#         }
#         async_to_sync(channel_layer.group_send)(f'{instance.calculation_record}', message)
# @receiver(post_save)
# def send_calculation_notification(sender, instance, created, **kwargs):
#     from lex.lex_app.logging.CalculationLog import CalculationLog
#     if created and sender == CalculationLog and instance.is_notification:
#         channel_layer = get_channel_layer()
#         message = {
#             'type': 'calculation_notification', # This is the correct naming convention
#             'payload': {
#                 'id': instance.id,
#                 'message': instance.message,
#             }
#         }
#         # notification = Notifications(message=instance.message, timestamp=datetime.now())
#         # notification.save()
#         async_to_sync(channel_layer.group_send)(f'calculation_notification', message)


def update_calculation_status(instance):
    from lex.lex_app.lex_models.CalculationModel import CalculationModel

    if issubclass(instance.__class__, CalculationModel) or issubclass(
        instance.__class__, UpdateModel
    ):
        channel_layer = get_channel_layer()
        message_type = ""
        if instance.is_calculated == CalculationModel.IN_PROGRESS:
            message_type = "calculation_in_progress"
        elif instance.is_calculated == CalculationModel.SUCCESS:
            message_type = "calculation_success"
        elif instance.is_calculated == CalculationModel.ERROR:
            message_type = "calculation_error"

        message = {
            "type": message_type,  # This is the correct naming convention
            "payload": {
                "record": str(instance),
                "record_id": f"{instance._meta.model_name}_{instance.id}",
            },
        }
        # notification = Notifications(message="Calculation is finished", timestamp=datetime.now())
        # notification.save()
        async_to_sync(channel_layer.group_send)(f"update_calculation_status", message)


def get_model_data(calculation_record, calculationId):
    from lex.lex_app.logging.CalculationLog import CalculationLog

    messages = []

    # Fetch messages from CalculationLog
    queryset_calc = CalculationLog.objects.filter(
        calculation_record=calculation_record, calculationId=calculationId
    ).only("timestamp", "message")
    messages.extend(
        f"{message.timestamp} {message.message}" for message in queryset_calc
    )

    return "\n".join(messages)


def do_post_save(sender, **kwargs):
    CalculatedModelUpdateHandler.register_save(kwargs["instance"])


from django.dispatch import Signal

custom_post_save = Signal()
