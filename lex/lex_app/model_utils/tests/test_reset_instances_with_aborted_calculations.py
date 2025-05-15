import os
import asyncio

import nest_asyncio
from django.db import connection
from django.test import TransactionTestCase

from lex.lex_app.lex_models.CalculationModel import CalculationModel
from lex.lex_app.model_utils.ModelRegistration import ModelRegistration
from lex.lex_app.ProcessAdminSettings import processAdminSite


class CalculationModelAbortTests(TransactionTestCase):
    # non-None → allow_cascade=True on flush; list must include your app + auth for Simple-History and User
    available_apps = ["lex_app"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        nest_asyncio.apply()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        processAdminSite.registered_models = {}

    def test_register_models_aborts_in_progress_instances(self):
        # 1) Define a short-lived CalculationModel subclass
        class AbortCalculationModel(CalculationModel):
            class Meta:
                app_label = "lex_app"
                managed = True

        # 2) Create its table right away (autocommit mode)
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(AbortCalculationModel)

        # 3) Turn off Celery, signal start-command
        os.environ.pop("CELERY_ACTIVE", None)
        os.environ["CALLED_FROM_START_COMMAND"] = "True"

        # 4) Seed an IN_PROGRESS instance (skip hooks)
        calc = AbortCalculationModel.objects.create(
            is_calculated=CalculationModel.NOT_CALCULATED
        )
        calc.is_calculated = CalculationModel.IN_PROGRESS
        calc.save(skip_hooks=True)

        # 5) This will internally do `loop.run_until_complete(...)` and abort IN_PROGRESS rows
        ModelRegistration.register_models([AbortCalculationModel])

        # 6) Check it really flipped to ABORTED
        calc.refresh_from_db()
        self.assertEqual(
            calc.is_calculated,
            CalculationModel.ABORTED,
            "IN_PROGRESS instances should be flipped to ABORTED",
        )
