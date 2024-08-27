import importlib
import os
import sys
from pathlib import Path

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib import admin
from lex.lex_app.model_utils.ModelRegistration import ModelRegistration


class GenericAppConfig(AppConfig):

    def ready(self):
        self.start(self.name)


    def start(self, repo_name=None):
        from lex.lex_app.streamlit.Streamlit import Streamlit

        self.model_structure = {}
        self.model_styling = {}
        self.global_filter_structure = {}
        self.widget_structure = []

        print('Name of the app', repo_name)
        if repo_name == 'lex_app':
            base_path = os.path.dirname(self.module.__file__)
        else:
            base_path = Path(os.getenv("PROJECT_ROOT")).resolve()
        self.pending_relationships = {}
        self.discovered_models = {}
        self.module = importlib.import_module(repo_name)
        self.path = base_path
        self.discover_models(self.path, repo_name=repo_name)
        self.resolve_relationships(repo_name=repo_name)
        self.register_models_with_admin()
        ModelRegistration.register_models([Streamlit])

    def discover_models(self, path, repo_name):
        for root, dirs, files in os.walk(path):
            # Skip 'venv', '.venv', and 'build' directories
            dirs[:] = [d for d in dirs if d not in ['venv', '.venv', 'build', 'migrations']]

            for file in files:
                # Process only .py files that do not start with '_'
                module_path = os.path.join(root, file)
                module_name = os.path.relpath(module_path, self.path)
                module_name = module_name.replace(os.path.sep, '.')[:-3]

                if repo_name == 'lex_app':
                    full_module_name = f"lex.{repo_name}.{module_name}"
                else:
                    full_module_name = f"{module_name}"

                if not self.is_special_file(file):
                    if file.endswith('model_structure.py'):
                        module = importlib.import_module(full_module_name)
                        if (hasattr(module, "get_model_structure")):
                            self.model_structure = module.get_model_structure()
                        if (hasattr(module, "get_widget_structure")):
                            self.widget_structure = module.get_widget_structure()
                        if (hasattr(module, "get_model_styling")):
                            self.model_styling = module.get_model_styling()
                        if (hasattr(module, "get_global_filter_structure")):
                            self.global_filter_structure = module.get_global_filter_structure()

                    else:  # Remove .py
                        # Skip specific modules
                        if module_name.split('.')[-1] in ["asgi", "wsgi", "settings", "urls", 'setup']:
                            continue

                        self.load_models_from_module(full_module_name)

    def load_models_from_module(self, full_module_name):
        from lex.lex_app.lex_models.html_report import HTMLReport

        try:
            print('Loading models from module', full_module_name)
            if not full_module_name.startswith('.'):
                module = importlib.import_module(full_module_name)
                for name, obj in module.__dict__.items():
                    if (isinstance(obj, type) and issubclass(obj, models.Model) and obj is not models.Model):
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

    def resolve_relationships(self, repo_name):
        for model_name, relationships in self.pending_relationships.items():
            model = self.discovered_models[model_name]
            for field_name, related_model_name in relationships:
                if '.' not in related_model_name:
                    related_model_name = f"{repo_name}.{related_model_name}"

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

    def register_models_with_admin(self):
        ModelRegistration.register_models(list(filter(lambda x: not admin.site.is_registered(x), self.discovered_models.values())))

        ModelRegistration.register_model_structure(self.model_structure)
        ModelRegistration.register_model_styling(self.model_styling)
        ModelRegistration.register_global_filter_structure(self.global_filter_structure)
        ModelRegistration.register_widget_structure(self.widget_structure)


    def is_special_file(self, file):
        file_without_extension = os.path.splitext(file)[0]

        return (file_without_extension.startswith("_") or
                file_without_extension.startswith(".") or
                file_without_extension.endswith("_test") or
                file_without_extension.endswith("create_db") or
                file_without_extension.endswith("Log") or
                # file_without_extension.endswith("Streamlit") or
                file_without_extension.endswith("CalculationIDs"))
