import os
import threading
import traceback
from datetime import datetime

from celery import current_task

from ProcessAdminRestApi.models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from ProcessAdminRestApi.views.model_entries import One
from generic_app import models
import inspect
from django.core.cache import cache

#### Note: Messages shall be delivered in the following format: "Severity: Message" The colon and the whitespace after are required for the code to work correctly ####
# Severity could be something like 'Error', 'Warning', 'Caution', etc. (See Static variables below!)


class CalculationLog(models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    trigger_name = models.TextField(null=True)
    message_type = models.TextField(default="")
    calculationId = models.TextField(default='test_id')
    message = models.TextField()
    method = models.TextField()
    is_notification = models.BooleanField(default=False)

    # Severities, to be concatenated with message in create statement
    SUCCESS = 'Success: '
    WARNING = 'Warning: '
    ERROR = 'Error: '
    START = 'Start: '
    FINISH = 'Finish: '

    # Message types
    PROGRESS = 'Progress'
    INPUT = 'Input Validation'
    OUTPUT = 'Output Validation'

    def save(self, *args, **kwargs):
        print(self.calculationId + ": " + self.message)
        if self.id is None:
            super(CalculationLog, self).save(*args, **kwargs)

    @classmethod
    def create(cls, message, message_type="Progress", trigger_name=None, is_notification=False):
        trace_objects = cls.get_trace_objects()

        if current_task and os.getenv("CELERY_ACTIVE"):
            calculation_id = cache.get(str(current_task.request.id).split("-")[0], "test_id")
        else:
            calculation_id = cache.get(threading.get_ident(), "test_id")

        calc_log = CalculationLog(timestamp=datetime.now(), method=str(trace_objects), message=message, calculationId=calculation_id, message_type=message_type,
                                  trigger_name=trigger_name, is_notification=is_notification)
        calc_log.save()

    @classmethod
    def get_calculation_id(cls, calculation_model):
        return f"{str(calculation_model._meta.model_name)}-{str(calculation_model.id)}" if calculation_model is not None else "test_id"

    @classmethod
    def get_trace_objects(cls):
        stack = list(traceback.extract_stack())
        currentframe = inspect.currentframe()
        trace_objects = []
        i = 0
        while currentframe is not None:
            if 'self' in currentframe.f_locals:
                tempobject = currentframe.f_locals['self']
            else:
                tempobject = None
            filename, methodname, lineno = stack[-(i + 1)].filename, stack[-(i + 1)].name, stack[-(i + 1)].lineno
            i += 1
            currentframe = currentframe.f_back
            if f"generic_app{os.sep}submodels" in filename and not "CalculationLog" in filename:
                trimmed_filename = filename.split(os.sep)[-1].split(".")[0]
                trace_objects.append((trimmed_filename, methodname, lineno, str(tempobject)))
        trace_objects.reverse()
        return trace_objects

    @classmethod
    def assertTrue(cls, assertion, message):
        if assertion:
            cls.create(message=message, message_type="Test: Success")
        else:
            cls.create(message=message, message_type="Test: Error")
