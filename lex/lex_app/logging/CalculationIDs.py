from lex.lex_app.models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from generic_app import models


class CalculationIDs(models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    context_id = models.TextField(default='test_id')
    calculation_record = models.TextField()
    calculation_id = models.TextField(default='test_id')