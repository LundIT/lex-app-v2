from django.test import TestCase
from django.db import connection, models


class AbstractModelTestCase(TestCase):
    test_model: type[models.Model] | None = None

    @classmethod
    def setUpClass(cls):
        if not cls.test_model:
            raise AttributeError(f"No test_model set for {cls.__name__}")
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(cls.test_model)
            # Also create the historical model's table
            schema_editor.create_model(cls.test_model.history.model)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(cls.test_model.history.model)
            schema_editor.delete_model(cls.test_model)
        super().tearDownClass()
