import json
from abc import abstractmethod
from datetime import datetime

from django.db import models
from django.db import transaction
from django.forms import model_to_dict
from django_lifecycle import hook, AFTER_UPDATE, AFTER_CREATE, BEFORE_UPDATE, BEFORE_CREATE, BEFORE_SAVE

from lex.lex_app.lex_models.LexModel import LexModel
from lex.lex_app.rest_api.signals import update_calculation_status
from lex.lex_app.lex_models.Revisions import Revisions


class CalculationModel(LexModel):

    IN_PROGRESS = 'IN_PROGRESS'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    NOT_CALCULATED = 'NOT_CALCULATED'
    ABORTED = 'ABORTED'
    STATUSES = [
        (IN_PROGRESS, 'IN_PROGRESS'),
        (ERROR, 'ERROR'),
        (SUCCESS, 'SUCCESS'),
        (NOT_CALCULATED, 'NOT_CALCULATED'),
        (ABORTED, 'ABORTED')
    ]

    is_calculated =  models.CharField(max_length=50, choices=STATUSES, default=NOT_CALCULATED, editable=False)

    class Meta:
        abstract = True

    @abstractmethod
    def calculate(self):
        pass

    # TODO: For the Celery task cases, this hook should be updated

    @hook(BEFORE_SAVE)
    def before_save(self):
        # Check if it's a new instance
        if self._state.adding:
            self.is_creation = True
        else:
            self.is_creation = False

    @hook(AFTER_UPDATE, on_commit=True)
    @hook(AFTER_CREATE, on_commit=True)
    def calculate_hook(self):
        update_calculation_status(self)
        try:
            if hasattr(self, 'is_atomic') and not self.is_atomic:
                self.calculate()
                self.is_calculated = self.SUCCESS
            else:
                with transaction.atomic():
                    self.calculate()
                    self.is_calculated = self.SUCCESS
        except Exception as e:
            self.is_calculated = self.ERROR
            raise e
        finally:
            self.save(skip_hooks=True)
            # TODO: Fix the bad code below
            if self.is_creation:
                action = "create"
                author_name = self.created_by if self.created_by == "Initial Data Upload" else \
                self.created_by.split(" (")[0]
                author_id = self.created_by if self.created_by == "Initial Data Upload" else \
                self.created_by.split(" (")[1].replace(")", "")
                payload = {"data": json.loads(json.dumps(model_to_dict(self), default=str))}
            else:
                previous_data = self.__class__.objects.filter(id=self.id).first()
                print("PREVIOUS DATA")
                print(previous_data)
                payload = {"data": json.loads(json.dumps(model_to_dict(self), default=str)),
                           "previousData": json.loads(json.dumps(model_to_dict(previous_data), default=str))}
                action = "update"
                author_name = self.edited_by.split(" (")[0] if self.edited_by else self.created_by.split(" (")[0]
                author_id = (self.edited_by.split(" (")[1].replace(")", "") if self.edited_by != "Initial Data Upload" else self.edited_by) if self.edited_by else \
                    self.created_by.split(" (")[1].replace(")", "")
            Revisions(authorId=author_name,
                      message=f"{datetime.now()}: Calculation is completed: {self.is_calculated}",
                      recordId=self.id,
                      date=datetime.now(),
                      resource=self._meta.model_name,
                      data=json.loads(json.dumps(model_to_dict(self), default=str)),
                      author={"id": author_id, "fullName": author_name},
                      payload=payload,
                      action=action).save()
            update_calculation_status(self)

