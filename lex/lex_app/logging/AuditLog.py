from django.db import models
from lex.lex_app.lex_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )
    modification_restriction = AdminReportsModificationRestriction()
    date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=255)
    resource = models.CharField(max_length=255)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    payload = models.JSONField(blank=True, null=True)
    calculation_id = models.TextField(default='test_id', null=True, blank=True)

    class Meta:
        app_label = 'lex_app'

    def __str__(self):
        return f"{self.action} on {self.resource} by {self.author}"

    def to_dict(self):
        """Convert log instance to dictionary with the format expected by the frontend."""
        return {
            "date": self.date.strftime('%Y-%m-%d %H:%M:%S'),
            "author": self.author,
            "resource": self.resource,
            "action": self.action,
            "payload": self.payload or {}
        }
