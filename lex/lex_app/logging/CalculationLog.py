import inspect
import os
import time
import traceback
from datetime import datetime
import logging

from celery import current_task
from django.db import models

from lex.lex_app import settings
from lex.lex_app.lex_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from lex.lex_app.logging.CalculationIDs import CalculationIDs
from lex.lex_app.rest_api.context import context_id
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from lex.lex_app.logging.AuditLog import AuditLog
from lex.lex_app.logging.model_context import _model_stack
from django.core.cache import caches
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
#### Note: Messages shall be delivered in the following format: "Severity: Message" The colon and the whitespace after are required for the code to work correctly ####
# Severity could be something like 'Error', 'Warning', 'Caution', etc. (See Static variables below!)

class CalculationLog(models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=datetime.now())
    calculationId = models.TextField(default='test_id')
    calculation_log = models.TextField(default="")
    calculationlog = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True) # parent calculation log
    auditlog = models.ForeignKey("AuditLog", on_delete=models.CASCADE, null=True, blank=True)
    # Generic fields to reference any calculatable object:
    # If you want to allow CalculationLog entries without a related instance,
    # consider setting null=True and blank=True. Otherwise, ensure an instance is always found.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    # This generic foreign key ties the above two fields, allowing dynamic reference.
    calculatable_object = GenericForeignKey('content_type', 'object_id')

    # Severities – to be concatenated with the message in the create statement
    SUCCESS = 'Success: '
    WARNING = 'Warning: '
    ERROR = 'Error: '
    START = 'Start: '
    FINISH = 'Finish: '

    # Message types
    PROGRESS = 'Progress'
    INPUT = 'Input Validation'
    OUTPUT = 'Output Validation'

    class Meta:
        app_label = 'lex_app'

    @classmethod
    def log(cls, message: str):
        """
        Logs `message` against the current model context:
        - current_model  = stack[-1]
        - parent_model   = stack[-2] (if present)
        """
        # 1) Grab the model stack
        stack = _model_stack.get()
        # if not stack:
        #     logging.getLogger("lex.calclog") \
        #         .warning("No model context for log: %s", message)
        #     return
        # 2) Resolve calculation_id & AuditLog
        calc_id = context_id.get()['calculation_id']
        redis_cache = caches['redis']
        audit_log = AuditLog.objects.get(calculation_id=calc_id)
        channel_layer = get_channel_layer()

        if len(stack) > 0:
            current_model = stack[-1]
            current_model_pk = current_model.pk
            # 3) Prepare CT and record string for current
            ctype_cur = ContentType.objects.get_for_model(current_model)
            current_record = f"{current_model._meta.model_name}_{current_model.pk}"

            calc_id_message = {
                'type': 'calculation_id',
                'payload': {
                    'calculation_record': current_record,
                    'calculation_id': calc_id
                }
            }
            async_to_sync(channel_layer.group_send)("calculations", calc_id_message)
        else:
            current_model = None
            current_model_pk = None
            ctype_cur = None
            current_record = None


        if len(stack) > 1:
            parent_model = stack[-2]
            if parent_model:
                ctype_par = ContentType.objects.get_for_model(parent_model)
                parent_record = f"{parent_model._meta.model_name}_{parent_model.pk}"

                parent_log, _ = cls.objects.get_or_create(
                    calculationId=calc_id,
                    auditlog=audit_log,
                    content_type=ctype_par,
                    object_id=parent_model.pk,
                )

                calc_id_message = {
                    'type': 'calculation_id',
                    'payload': {
                        'calculation_record': parent_record,
                        'calculation_id': calc_id
                    }
                }
                async_to_sync(channel_layer.group_send)("calculations", calc_id_message)
        else:
            parent_log = None


        # 4) If we have a parent, ensure its log exists first


        log_entry, _ = cls.objects.get_or_create(
            calculationId=calc_id,
            auditlog=audit_log,
            content_type=ctype_cur,
            object_id=current_model_pk,
            calculationlog=parent_log,
        )

        # 5) Append & save
        log_entry.calculation_log = (log_entry.calculation_log or "") + f"\n{message}"
        log_entry.save()



        redis_cache.set(
            f"{current_record}_{calc_id}",
            redis_cache.get(f"{current_record}_{calc_id}", "") + "\n" + message,
            timeout=60 * 60 * 24 * 7,  # Cache for one week
        )
        # 6) Also emit to your WebSocket/logger
        logging.getLogger("lex.calclog").debug(
            message,
            extra={
                "calculation_record": current_record,
                "calculationId": calc_id,
            },
        )


    # def save(self, *args, **kwargs):
    #     print(self.calculationId + ": " + self.message)
    #     # Only execute the parent save if the instance is new (id is None)
    #     if self.id is None:
    #         super(CalculationLog, self).save(*args, **kwargs)

    def to_dict(self):
        """
        Return a dictionary representation of the CalculationLog that is JSON serializable.
        Note: Instead of returning the raw calculatable_object (which is a Django model instance),
        we return a representation containing the related model name, object id, and its string representation.
        """
        return {
            'calculationId': self.calculationId,
            'logId': self.id,
            'calculation_record': self.calculation_record,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'trigger_name': self.trigger_name,
            # Represent the related object safely:
            'calculatable_object': {
                'model': self.content_type.model if self.content_type else None,
                'object_id': self.object_id,
                'display': str(self.calculatable_object) if self.calculatable_object else None
            },
            'method': self.method,
            'is_notification': self.is_notification,
            'message_type': self.message_type,
            'detailed_message': self.detailed_message
        }

    @classmethod
    def create(cls, message, details="", message_type="Progress", trigger_name=None, is_notification=False):
        # Get tracing details including the first (calculatable) instance found
        trace_results = cls.get_trace_objects()
        trace_objects = trace_results["trace_objects"]
        # Now, first_model_instance holds the actual Django model instance, not just a string.
        first_model_instance = trace_results["first_model_instance"]

        if first_model_instance:
            # Generate a string record for logging from the instance.
            calculation_record = f"{first_model_instance._meta.model_name}_{first_model_instance.pk}"
            # Automatically attach the related generic key values.
            content_type = ContentType.objects.get_for_model(first_model_instance)
            object_id = first_model_instance.pk
        else:
            # Fallback if no suitable instance was found.
            calculation_record = "init_upload"
            # Here you may decide on a dummy value or consider making the FK fields optional.
            content_type = None
            object_id = None

        # Retrieve or create the CalculationIDs record using the calculated record string.
        # if current_task and os.getenv("CELERY_ACTIVE"):
        #     print(current_task.request.id)
        #     obj, created = CalculationIDs.objects.get_or_create(
        #         calculation_record=calculation_record if calculation_record else "init_upload",
        #         calculation_id=str(current_task.request.id),
        #         defaults={
        #             'context_id': getattr(
        #                 CalculationIDs.objects.filter(calculation_id=str(current_task.request.id)).first(),
        #                 "context_id", "test_id")
        #         }
        #     )
        #     calculation_id = getattr(obj, "calculation_id", "test_id")
        # else:
        obj, created = CalculationIDs.objects.get_or_create(
                calculation_record=calculation_record if calculation_record else "init_upload",
                context_id=context_id.get()['context_id'] if context_id.get() else "test_id",
                defaults={
                    'calculation_id': getattr(
                        CalculationIDs.objects.filter(context_id=context_id.get()['context_id']).first(),
                        "calculation_id", "test_id")
                }
            )
        calculation_id = getattr(obj, "calculation_id", "test_id")

        # Create the CalculationLog, now including the generic relationship fields if available.
        calc_log = CalculationLog(
            timestamp=datetime.now(),
            method=str(trace_objects),
            calculation_record=calculation_record if calculation_record else "init_upload",
            message=message,
            calculationId=calculation_id,
            message_type=message_type,
            trigger_name=trigger_name,
            is_notification=is_notification,
            detailed_message=details,
            content_type=content_type,
            object_id=object_id,
        )

        calc_log.save()
        return calc_log

    @classmethod
    def get_calculation_id(cls, calculation_model):
        return f"{str(calculation_model._meta.model_name)}-{str(calculation_model.id)}" if calculation_model is not None else "test_id"

    @classmethod
    def get_trace_objects(cls):
        """
        Walk the call stack to retrieve a list of trace objects and extract the first Django model
        instance encountered (which is assumed to be the calculation instance). Additionally,
        if available, retrieve the very first caller model class instance that appears in the call stack.
        In this implementation, all Django model instances encountered are recorded and then:
          - the innermost one (first encountered during the upward walk) is treated as the calculation instance,
          - the outermost one (last in the list) is considered the caller that triggered everything.
        """

        stack = list(traceback.extract_stack())
        currentframe = inspect.currentframe()
        trace_objects = []
        trace_objects_class_list = []
        model_instances = []  # Will accumulate Django model instances (objects with _meta).
        i = 0

        while currentframe is not None:
            if 'self' in currentframe.f_locals:
                tempobject = currentframe.f_locals['self']
            else:
                tempobject = None

            # Use the stack list to get file, method name, and line number.
            filename = stack[-(i + 1)].filename
            methodname = stack[-(i + 1)].name
            lineno = stack[-(i + 1)].lineno
            i += 1

            # Move to the next outer frame.
            currentframe = currentframe.f_back

            # Only consider frames from your repository and not part of CalculationLog itself.
            if f"{settings.repo_name}" in filename and "CalculationLog" not in filename:
                trimmed_filename = filename.split(os.sep)[-1].split(".")[0]

                if tempobject and hasattr(tempobject, "_meta"):
                    # Append any Django model instance to our list.
                    model_instances.append(tempobject)

                trace_objects.append((trimmed_filename, methodname, lineno, str(tempobject)))
                if tempobject and hasattr(tempobject, "_meta"):
                    trace_objects_class_list.append(tempobject._meta.model_name)

        # Reverse the trace list so it goes from earliest to latest (for reporting purposes).
        trace_objects.reverse()

        # Set first_model_instance to the model nearest to the current context (calculation instance)
        # and caller_model_instance to the very outer-most model instance (the one that triggered everything).
        first_model_instance = model_instances[0] if model_instances else None

        # Only treat the outermost as a caller if it’s different from the first
        if len(model_instances) > 1 and model_instances[-1] is not first_model_instance:
            caller_model_instance = model_instances[-1]
        else:
            caller_model_instance = None

        result = {
            "trace_objects": trace_objects,
            "first_model_instance": first_model_instance,
            "caller_model_instance": caller_model_instance,
            "trace_objects_class_list": list(set(trace_objects_class_list))
        }
        return result

    @classmethod
    def assertTrue(cls, assertion, message):
        if assertion:
            cls.create(message=message, message_type="Test: Success")
        else:
            cls.create(message=message, message_type="Test: Error")
