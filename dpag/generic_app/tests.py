from django.test import TestCase

# Create your tests here.
from django.db import models
# Create your models here.
from django.db.models import Model, AutoField, TextField, FloatField, DateTimeField, ForeignKey, CASCADE
from ProcessAdminRestApi.models.calculated_model import CalculatedModelMixin
from ProcessAdminRestApi.models.upload_model import UploadModelMixin
import os
from glob import glob
from pathlib import Path

from django.db.models.signals import post_save
from django.dispatch import receiver
from DjangoProcessAdminGeneric.ProcessAdminSettings import processAdminSite, adminSite

# Find all files in submodels and import them via exec
# Find the app name as the nameof the directory this file is in
app_name = Path(__file__).resolve().parent.parts[-1]
# Find all files in submodels
files = list(Path(__file__).resolve().parent.glob("submodels/**/*_test.py"))
for i, file in enumerate(files):
    if file.stem.endswith("_test"):
        # Get the name of file
        name = file.stem
        subfolders = '.'.join(file.parts[file.parts.index('submodels')+1:-1])
        try:
            #TODO ensure that no wrong things can be imported here. #Security Issue
            exec(f"from {app_name}.submodels.{subfolders}.{name} import {name}")
            imported_class = eval(name)

        except NameError:
            # If the current file can't be imported, put it in the end of the line hoping that we will clear the dependecies later
            if not i>=len(files)-1:
                files.append(file)

