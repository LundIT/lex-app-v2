from pathlib import Path
from typing import Dict, Type, List
from django.db import models
import os


class ModelStructureBuilder:
    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.model_structure: Dict = {}

    def build_structure(self, models: List[Type[models.Model]]) -> Dict:
        for model in models:
            path = self._get_model_path(model)
            self._insert_model_to_structure(path, model._meta.model_name)

        self._shorten_model_structure()
        self._add_reports_to_structure()
        return self.model_structure

    def _get_model_path(self, model: Type[models.Model]) -> str:
        module_parts = model.__module__.split('.')
        repo_index = module_parts.index(self.repo_name)
        return '.'.join(module_parts[repo_index + 1:-1])

    def _insert_model_to_structure(self, path: str, name: str):
        current = self.model_structure
        for p in path.split('.'):
            if p not in current:
                current[p] = {}
            current = current[p]
        current[name] = None

    def _shorten_model_structure(self):
        self.model_structure = self._shorten_dict(self.model_structure)

    def _shorten_dict(self, d: Dict) -> Dict:
        while len(d) == 1 and isinstance(next(iter(d.values())), dict):
            d = next(iter(d.values()))
        return d

    def _add_reports_to_structure(self):
        self.model_structure['Z_Reports'] = {'userchangelog': None, 'calculationlog': None, 'log': None}
        if os.getenv("IS_STREAMLIT_ENABLED") == "true":
            self.model_structure['Streamlit'] = {'streamlit': None}
