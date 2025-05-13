from lex.lex_app.lex_models.tests.factories.LexModel_factory import (
    DummyLexModel,
    LexModelFactory,
)

from lex.lex_app.lex_models.tests.models.abstract_model_test_case import (
    AbstractModelTestCase,
)


class TestLexModel(AbstractModelTestCase):
    test_model = DummyLexModel

    def test_initial_instantiation(self):
        model = LexModelFactory.create()
        self.assertEqual(model.created_by, "Initial Data Upload")
        self.assertEqual(model.edited_by, None)

    def test_edit_instance(self):
        model = LexModelFactory.create()
        model.dummy_field = "New Value"
        model.save()
        self.assertEqual(model.created_by, "Initial Data Upload")
        self.assertEqual(model.edited_by, "Initial Data Upload")
