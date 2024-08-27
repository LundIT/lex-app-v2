import importlib
import os
import sys
from pathlib import Path

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib import admin

class GenericAppConfig(AppConfig):
    def ready(self):
        base_path = Path(os.getenv("PROJECT_ROOT")).resolve()
        self.pending_relationships = {}
        self.discovered_models = {}
        self.module = importlib.import_module(self.name)
        self.path = base_path
        self.discover_models(self.path)
        self.resolve_relationships()
        self.register_models_with_admin()

    def discover_models(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.py') and not file.startswith('_'):
                    module_path = os.path.join(root, file)
                    module_name = os.path.relpath(module_path, self.path)
                    module_name = module_name.replace(os.path.sep, '.')[:-3]  # Remove .py
                    full_module_name = f"{self.name}.{module_name}"
                    if module_name in ["asgi", "wsgi", "settings", "urls"]:
                        continue

                    self.load_models_from_module(full_module_name)

    def load_models_from_module(self, full_module_name):
        try:
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

    def resolve_relationships(self):
        for model_name, relationships in self.pending_relationships.items():
            model = self.discovered_models[model_name]
            for field_name, related_model_name in relationships:
                if '.' not in related_model_name:
                    related_model_name = f"{self.name}.{related_model_name}"

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
        for model in self.discovered_models.values():
            if not admin.site.is_registered(model):
                admin.site.register(model)
