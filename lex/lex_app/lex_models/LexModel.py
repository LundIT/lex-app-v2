from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE, AFTER_CREATE
from lex.lex_app.rest_api.context import context_id
from django.db import models


class LexModel(LifecycleModel):
    
    created_by = models.TextField(null=True, blank=True, editable=False)
    edited_by = models.TextField(null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    @hook(AFTER_UPDATE)
    def update_edited_by(self):
        self.edited_by = f"{context_id.get()['request_obj'].auth['name']} ({context_id.get()['request_obj'].auth['sub']})"

    @hook(AFTER_CREATE)
    def update_created_by(self):
        self.created_by = f"{context_id.get()['request_obj'].auth['name']} ({context_id.get()['request_obj'].auth['sub']})"