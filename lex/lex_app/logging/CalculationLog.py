import inspect
import os
import time
import traceback
from datetime import datetime

from celery import current_task
from django.db import models

from lex.lex_app import settings
from lex.lex_app.lex_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from lex.lex_app.logging.CalculationIDs import CalculationIDs
from lex.lex_app.rest_api.context import context_id
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from lex.lex_app.logging.AuditLog import AuditLog


#### Note: Messages shall be delivered in the following format: "Severity: Message" The colon and the whitespace after are required for the code to work correctly ####
# Severity could be something like 'Error', 'Warning', 'Caution', etc. (See Static variables below!)

class CalculationLog(models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=datetime.now())
    trigger_name = models.TextField(null=True)
    message_type = models.TextField(default="")
    detailed_message = models.TextField("")
    calculationId = models.TextField(default='test_id')
    calculation_record = models.TextField(default="legacy")
    message = models.TextField(default="")
    method = models.TextField(default="")
    is_notification = models.BooleanField(default=False)
    calculationlog = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
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
    # @classmethod
    # def get_parent_log(self, audit_log):
    #     trace_results = CalculationLog.get_trace_objects()
    #     first_model_instance = trace_results["first_model_instance"]
    #     ctype = ContentType.objects.get_for_model(first_model_instance)
    #     parent_logs = CalculationLog.objects.filter(content_type=ctype, object_id=first_model_instance.pk, audit_log=self.audit_log)
    #     return parent_logs.first()

    @classmethod
    def log(cls, message="", details="", message_type="Progress", trigger_name=None, is_notification=False):
        trace_results = CalculationLog.get_trace_objects()
        trace_objects = trace_results["trace_objects"]
        first_model_instance = trace_results["first_model_instance"]
        caller_model_instance = trace_results["caller_model_instance"]
        calculation_id = context_id.get()['calculation_id'] # from context

        ctype_first_model_instance = ContentType.objects.get_for_model(first_model_instance)

        audit_log = AuditLog.objects.get(calculation_id=calculation_id)

        calculation_record = f"{first_model_instance._meta.model_name}_{first_model_instance.pk}"

        if caller_model_instance is None:
            calc_log, is_calc_log_created = CalculationLog.objects.get_or_create(calculationId=calculation_id,
                                                                     auditlog=audit_log,
                                                                     content_type=ctype_first_model_instance,
                                                                     object_id=first_model_instance.pk,
                                                                     )
            calc_log.message += f"\n {message}"
            calc_log.save()
        else:
            ctype_caller_model_instance = ContentType.objects.get_for_model(caller_model_instance)
            parent_calc_log, is_parent_calc_log_created = CalculationLog.objects.get_or_create(calculationId=calculation_id,
                                                                     auditlog=audit_log,
                                                                     content_type=ctype_caller_model_instance,
                                                                     object_id=caller_model_instance.pk)

            calc_log, created = CalculationLog.objects.get_or_create(calculationId=calculation_id,
                                                                     auditlog=audit_log,
                                                                     content_type=ctype_first_model_instance,
                                                                     object_id=first_model_instance.pk,
                                                                     calculationlog=parent_calc_log)

            calc_log.message += f"\n {message}"
            calc_log.save()

        # calc_log = CalculationLog(
        #     timestamp=datetime.now(),
        #     method=str(trace_objects),
        #     calculation_record=calculation_record if calculation_record else "init_upload",
        #     message=message,
        #     calculationId=calculation_id,
        #     message_type=message_type,
        #     trigger_name=trigger_name,
        #     is_notification=is_notification,
        #     detailed_message=details,
        #     content_type=ctype,
        #     object_id=first_model_instance.pk,
        #     parent_calculation_log=parent_calculation_log,
        #     audit_log=audit_log
        # )
        #
        # calc_log.save()


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
        """

        stack = list(traceback.extract_stack())
        currentframe = inspect.currentframe()
        trace_objects = []
        trace_objects_class_list = []
        first_model_instance = None  # The first encountered Django model instance.
        caller_model_instance = None  # The first caller model instance found after the first.
        i = 0

        while currentframe is not None:
            if 'self' in currentframe.f_locals:
                tempobject = currentframe.f_locals['self']
            else:
                tempobject = None

            # Extract filename, method name, and line number from the stack.
            filename, methodname, lineno = stack[-(i + 1)].filename, stack[-(i + 1)].name, stack[-(i + 1)].lineno
            i += 1

            # Move up in the call stack.
            currentframe = currentframe.f_back

            # Only consider frames from your repository that are not part of CalculationLog itself.
            if f"{settings.repo_name}" in filename and "CalculationLog" not in filename:
                trimmed_filename = filename.split(os.sep)[-1].split(".")[0]

                if tempobject and hasattr(tempobject, "_meta"):
                    # If no Django model instance has been saved yet, do so.
                    if first_model_instance is None:
                        first_model_instance = tempobject
                    # Otherwise, if we haven't yet recorded a caller model instance and the current one is different,
                    # then set it as the caller.
                    elif caller_model_instance is None and tempobject is not first_model_instance:
                        caller_model_instance = tempobject

                trace_objects.append((trimmed_filename, methodname, lineno, str(tempobject)))
                if hasattr(tempobject, "_meta"):
                    trace_objects_class_list.append(tempobject._meta.model_name)

        # Reverse the trace list to order it from earliest to latest.
        trace_objects.reverse()

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
