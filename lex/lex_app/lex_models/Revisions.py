from django.db import models

class Revisions(models.Model):
    id = models.AutoField(primary_key=True)  # Primary key
    resource = models.CharField(max_length=255)  # Name of the resource
    recordId = models.CharField(max_length=255, null=True, blank=True)  # ID of the record being revised
    date = models.DateTimeField(auto_now_add=True)  # Automatically set the date to now
    message = models.CharField(max_length=255, blank=True)  # Short message
    description = models.TextField(null=True, blank=True)  # Long description
    authorId = models.CharField(max_length=255, null=True, blank=True)  # ForeignKey to User model
    data = models.JSONField(default=dict, null=True, blank=True)  # JSON data of the revision

    # Audit specific fields
    author = models.JSONField(default=dict, null=True, blank=True)  # Name of the author
    action = models.CharField(max_length=255, default="update")  # Action performed
    payload = models.JSONField(default=dict, null=True, blank=True)  # JSON data of the action

    class Meta:
        app_label = 'lex_app'

    def __str__(self):
        return f'Revision {self.recordId} by {self.authorId} on {self.date}'