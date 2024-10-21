from django.db import models
from django_lifecycle import LifecycleModel

from lex.lex_app.lex_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction


class UserChangeLog(LifecycleModel):
    modification_restriction = AdminReportsModificationRestriction()
    id = models.AutoField(primary_key=True)
    user_name = models.TextField()
    timestamp = models.DateTimeField()
    message = models.TextField()
    traceback = models.TextField(default="", null=True)
    calculationId = models.TextField(default='-1')
    calculation_record = models.TextField(default="legacy")

    class Meta:
        app_label = 'lex_app'

    def save(self, *args, **kwargs):
        if self.id is None:
            super(UserChangeLog, self).save(*args, **kwargs)
    #
    # @hook(AFTER_SAVE, on_commit=True)
    # def create_user_change_log(self):
    #     builder = LexLogger().builder() \
    #         .add_heading("User Change Log", level=2) \
    #         .add_paragraph(f"**User Name:** {self.user_name}") \
    #         .add_paragraph(f"**Timestamp:** {self.timestamp}") \
    #         .add_paragraph(f"**Message:** {self.message}") \
    #         .add_paragraph(f"**Calculation ID:** {self.calculationId}") \
    #         .add_paragraph(f"**Calculation Record:** {self.calculation_record}")
    #     # Optionally add a traceback if available
    #     if self.traceback:
    #         builder.add_heading("Traceback", level=3)
    #         builder.add_code_block(self.traceback)
    #
    #     builder.log(class_name="UserChangeLog")
