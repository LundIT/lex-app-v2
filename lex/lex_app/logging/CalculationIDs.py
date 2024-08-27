from lex.lex_app.lex_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from django.db import models


class CalculationIDs(models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    context_id = models.TextField(default='test_id')
    calculation_record = models.TextField()
    calculation_id = models.TextField(default='test_id')

    class Meta:
        app_label = 'lex_app'