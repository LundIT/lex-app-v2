from django.db import models
import factory

from lex.lex_app.lex_models.LexModel import LexModel


class DummyLexModel(LexModel):
    class Meta:
        app_label = "lex_app"
        managed = True

    dummy_field = models.CharField()


class LexModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DummyLexModel
