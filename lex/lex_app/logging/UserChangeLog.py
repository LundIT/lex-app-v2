from lex.lex_app.models.ModificationRestrictedModelExample import AdminReportsModificationRestriction
from generic_app import models


class UserChangeLog(models.Model):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    user_name = models.TextField()
    timestamp = models.DateTimeField()
    message = models.TextField()
    traceback = models.TextField(default="", null=True)
    calculationId = models.TextField(default='-1')
    calculation_record = models.TextField(default="legacy")

    def save(self, *args, **kwargs):
        if self.id is None:
            super(UserChangeLog, self).save(*args, **kwargs)