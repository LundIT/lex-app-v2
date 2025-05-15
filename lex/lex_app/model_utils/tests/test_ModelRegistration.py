# tests/test_model_registration.py
import os
from django.test import TestCase
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.db import connection

from lex.lex_app.ProcessAdminSettings import processAdminSite
from lex.lex_app.model_utils.ModelRegistration import ModelRegistration
from lex.lex_app.lex_models.Process import Process
from lex.lex_app.lex_models.html_report import HTMLReport
from lex.lex_app.lex_models.CalculationModel import CalculationModel


class ModelRegistrationTests(TestCase):
    def setUp(self):
        # 1) Clear any ENV flags
        os.environ.pop("CALLED_FROM_START_COMMAND", None)
        os.environ.pop("CELERY_ACTIVE", None)

        # 2) Reset processAdminSite to pristine state
        processAdminSite.registered_models = {}
        processAdminSite.html_reports = {}
        processAdminSite.processes = {}
        processAdminSite.model_structure = {}
        processAdminSite.model_styling = {}
        processAdminSite.widget_structure = []
        processAdminSite.initialized = False
        processAdminSite.model_collection = None

        # 3) Reset the real Django admin registry
        admin.site._registry = {}

    def test_user___str___override_and_process_admin_registration(self):
        # Before registration, __str__ is the default (uses username)
        if "__str__" in User.__dict__:
            delattr(User, "__str__")

        u = User(first_name="A", last_name="B", username="foo")
        self.assertNotEqual(str(u), "A B")

        ModelRegistration.register_models([User])

        # After, __str__ is our f"{first_name} {last_name}"
        u2 = User(first_name="A", last_name="B", username="foo")
        self.assertEqual(str(u2), "A B")

        # And User must now be in processAdminSite.registered_models
        self.assertIn(User, processAdminSite.registered_models)

    def test_html_report_subclass_registration(self):
        class StubReport(HTMLReport):
            pass

        ModelRegistration.register_models([StubReport])

        # HTMLReport subclasses go into .html_reports by lower‐cased name
        self.assertIn("stubreport", processAdminSite.html_reports)
        self.assertIs(processAdminSite.html_reports["stubreport"], StubReport)

        # And also into the main .registered_models with a ModelProcessAdmin
        self.assertIn(StubReport, processAdminSite.registered_models)

    def test_process_subclass_registration(self):
        class StubProc(Process):
            class Meta:
                app_label = "lex_app"
                managed = True

        ModelRegistration.register_models([StubProc])

        # Process subclasses go into .processes by lower‐cased name
        self.assertIn("stubproc", processAdminSite.processes)
        self.assertIs(processAdminSite.processes["stubproc"], StubProc)

        # And also into .registered_models
        self.assertIn(StubProc, processAdminSite.registered_models)

    def test_plain_model_gets_history_and_admin(self):
        # minimal model stub
        class Plain(models.Model):
            class Meta:
                app_label = "lex_app"
                managed = True

        ModelRegistration.register_models([Plain])

        # we get a Plain.history attribute, pointing to a Historical model
        self.assertTrue(hasattr(Plain, "history"))
        hist_model = Plain.history.model

        # That history model must also be in processAdminSite
        self.assertIn(hist_model, processAdminSite.registered_models)
        # And the original Plain must be in real Django admin
        self.assertIn(Plain, admin.site._registry)

    def test_calculation_model_skips_abort_when_flag_false(self):
        # set the flag to "False" → should skip abort logic
        os.environ["CALLED_FROM_START_COMMAND"] = "False"
        os.environ.pop("CELERY_ACTIVE", None)

        class SkipAbortCalculationModel(CalculationModel):
            class Meta:
                app_label = "lex_app"
                managed = True

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(SkipAbortCalculationModel)

        calc = SkipAbortCalculationModel.objects.create(
            is_calculated=CalculationModel.NOT_CALCULATED
        )
        calc.is_calculated = CalculationModel.IN_PROGRESS
        calc.save(skip_hooks=True)

        ModelRegistration.register_models([SkipAbortCalculationModel])

        self.assertEqual(
            calc.is_calculated,
            CalculationModel.IN_PROGRESS,
            "Without CALLED_FROM_START_COMMAND, we should skip aborting",
        )

    def test_register_model_structure_and_styling_and_widget(self):
        struct = {"Model": {"model": None}}
        style = {"Model Name": {"name": "Model Name Readable"}}
        # TODO: Remove widget test after removing the widgeting feature from the lex-app
        widget = [{"foo": "bar"}]

        ModelRegistration.register_model_structure(struct)
        ModelRegistration.register_model_styling(style)
        ModelRegistration.register_widget_structure(widget)

        self.assertEqual(processAdminSite.model_structure, struct)
        self.assertEqual(processAdminSite.model_styling, style)
        self.assertEqual(processAdminSite.widget_structure, widget)
