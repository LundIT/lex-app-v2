# Create your models here.
from django.db import models

from lex.lex_app.lex_models.ModificationRestrictedModelExample import AdminReportsModificationRestriction

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    overview = models.TextField(blank=True, null=True)
    input_files = models.ManyToManyField('ProjectInputFiles')
    output_files = models.ManyToManyField('ProjectOutputFiles')
    structure = models.JSONField(blank=True, null=True)
    components = models.JSONField(blank=True, null=True)
    models_fields = models.TextField(blank=True, null=True)
    business_logic_calcs = models.TextField(blank=True, null=True)
    db_table_field_mapping = models.TextField(blank=True, null=True)
    specification_doc = models.TextField(blank=True, null=True)
    generated_code = models.TextField(blank=True, null=True)


    class Meta:
        app_label = 'lex_ai'

class ProjectInputFiles(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='files/')
    explanation = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'lex_ai'

class ProjectOutputFiles(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='files/')
    explanation = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'lex_ai'