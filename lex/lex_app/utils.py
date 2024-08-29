import importlib
import os
import sys
from pathlib import Path

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib import admin
from lex.lex_app.model_utils.ModelRegistration import ModelRegistration
from lex.lex_app.model_utils.ModelStructureBuilder import ModelStructureBuilder


def create_api_key():
    try:
        from rest_framework_api_key.models import APIKey
        if APIKey.objects.count() == 0:
            api_key, key = APIKey.objects.create_key(name='APIKey')
            print("API_KEY:", key)
        else:
            print("API_KEY already exists")
    except ImportError as e:
        print(f"Error importing APIKey: {e}")


class GenericAppConfig(AppConfig):
    _EXCLUDED_FILES = ("asgi", "wsgi", "settings", "urls", 'setup')
    _EXCLUDED_DIRS = ('venv', '.venv', 'build', 'migrations')
    _EXCLUDED_PREFIXES = ('_', '.')
    _EXCLUDED_POSTFIXES = ('_', '.', 'create_db', 'CalculationIDs', '_test')

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.subdir = None
        self.project_path = None
        self.model_structure_builder = None
        self.pending_relationships = None
        self.discovered_models = None

    def ready(self):
        self.start(repo=self.name, subdir=f"lex.{self.name}.")

    def start(self, repo=None, subdir=""):
        self.pending_relationships = {}
        self.discovered_models = {}
        self.model_structure_builder = ModelStructureBuilder(repo=repo)
        self.project_path = os.path.dirname(self.module.__file__) if subdir else Path(
            os.getenv("PROJECT_ROOT")).resolve()
        self.subdir = f"" if not subdir else subdir

        self.discover_models(self.project_path, repo=repo)
        self.resolve_relationships(repo=repo)

        if not self.model_structure_builder.model_structure and not subdir:
            self.model_structure_builder.build_structure(self.discovered_models)

        self.register_models_with_admin()

        if sys.argv[1:2] == ["runserver"]:
            create_api_key()

    # Extracting models from the valid python files, and processing them one by one
    def discover_models(self, path, repo):
        for root, dirs, files in os.walk(path):
            # Skip 'venv', '.venv', and 'build' directories
            dirs[:] = [directory for directory in dirs if self._dir_filter(directory)]
            for file in files:
                # Process only .py files that do not start with '_'

                absolute_path = os.path.join(root, file)
                module_name = os.path.relpath(absolute_path, self.project_path)
                rel_module_name = module_name.replace(os.path.sep, '.')[:-3]
                module_name = rel_module_name.split('.')[-1]
                full_module_name = f"{self.subdir}{rel_module_name}"

                if self._is_valid_module(module_name, file):
                    self._process_module(full_module_name, file)

    def _dir_filter(self, directory):
        return directory not in self._EXCLUDED_DIRS

    def _is_valid_module(self, module_name, file):
        return (file.endswith('.py') and
                not module_name.startswith(self._EXCLUDED_PREFIXES) and
                not module_name.endswith(self._EXCLUDED_POSTFIXES) and
                module_name not in self._EXCLUDED_FILES)

    def _process_module(self, full_module_name, file):
        if file.endswith('model_structure.py'):
            self.model_structure_builder.extract_and_save_structure(full_module_name)
        elif file.endswith('_authentication_settings.py'):
            try:
                module = importlib.import_module(full_module_name)
                module.create_groups()
            except ImportError as e:
                print(f"Error importing authentication settings: {e}")
            except Exception as e:
                print(f"Authentication settings doesn't have method create_groups()")
        else:
            self.load_models_from_module(full_module_name)

    def load_models_from_module(self, full_module_name):
        from lex.lex_app.lex_models.html_report import HTMLReport
        try:
            print('Loading models from module', full_module_name)
            if not full_module_name.startswith('.'):
                module = importlib.import_module(full_module_name)
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, models.Model) and obj is not models.Model:
                        if not obj._meta.abstract:
                            self.add_model(name, obj)
        except ImportError as e:
            print(f"Error importing {full_module_name}: {e}")

    def add_model(self, name, model):
        if name not in self.discovered_models:
            self.discovered_models[name] = model
            self.pending_relationships[name] = []

            for field in model._meta.fields + model._meta.many_to_many:
                if isinstance(field, models.ForeignKey) or isinstance(field, models.ManyToManyField):
                    related_model = field.remote_field.model
                    if isinstance(related_model, str):
                        self.pending_relationships[name].append((field.name, related_model))

    def resolve_relationships(self, repo):
        for model_name, relationships in self.pending_relationships.items():
            model = self.discovered_models[model_name]
            for field_name, related_model_name in relationships:
                if '.' not in related_model_name:
                    related_model_name = f"{repo}.{related_model_name}"

                try:
                    related_model = self.get_model_c(related_model_name)
                    field = model._meta.get_field(field_name)
                    field.remote_field.model = related_model
                except LookupError:
                    raise ImproperlyConfigured(
                        f"Related model '{related_model_name}' for '{model_name}.{field_name}' not found")

    def get_model_c(self, model_name):
        if '.' in model_name:
            app_label, model_name = model_name.split('.')
            try:
                return self.apps.get_model(app_label, model_name)
            except AttributeError:
                return self.apps.get_app_config(app_label).get_model(model_name)
        return self.discovered_models.get(model_name)

    # All model Registrations happen here
    def register_models_with_admin(self):
        from lex_app.streamlit.Streamlit import Streamlit

        ModelRegistration.register_models(
            [o for o in self.discovered_models.values() if not admin.site.is_registered(o)])

        ModelRegistration.register_model_structure(self.model_structure_builder.model_structure)
        ModelRegistration.register_model_styling(self.model_structure_builder.model_styling)
        ModelRegistration.register_global_filter_structure(self.model_structure_builder.global_filter_structure)
        ModelRegistration.register_widget_structure(self.model_structure_builder.widget_structure)
        ModelRegistration.register_models([Streamlit])
