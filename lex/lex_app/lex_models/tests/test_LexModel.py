from django.test import TestCase

from lex.lex_app.lex_models.tests.factories.LexModel_factory import (
    DummyLexModel,
    LexModelFactory,
)
from django.db import connection


class TestLexModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(DummyLexModel)
            # Also create the historical model's table
            schema_editor.create_model(DummyLexModel.history.model)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(DummyLexModel.history.model)
            schema_editor.delete_model(DummyLexModel)
        super().tearDownClass()

    def test_default_fields(self):
        model = LexModelFactory.create()
