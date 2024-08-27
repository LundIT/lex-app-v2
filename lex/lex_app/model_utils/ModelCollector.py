import importlib
import os
from pathlib import Path
from typing import List, Type
from django.db.models import Model

class ModelCollector:
    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.collected_models = []
        self.model_structure = {}
        self.model_styling = {}
        self.global_filter_structure = {}

    def import_and_collect_models(self, file_paths: List[Path]) -> List[Type[Model]]:
        for file_path in file_paths:
            if self._is_special_file(file_path):
                continue

            # subfolders = '.'.join(file.parts[file.parts.index(repo_name) + 1:-1])
            module_name = self._get_module_name(file_path)
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Model) and not attr._meta.abstract:
                        self.collected_models.append(attr)
            except ImportError as e:
                print(f"Error importing {module_name}: {e}")

        return self.collected_models

    def _is_special_file(self, file: Path) -> bool:
        return (file.stem.endswith("_test") or
                file.parents[0].name == "migrations" or
                file.stem.endswith("create_db") or
                file.stem.endswith("Log") or
                file.stem.endswith("Streamlit") or
                file.stem.endswith("CalculationIDs"))

    def _get_module_name(self, file_path: Path) -> str:
        parts = file_path.parts
        repo_index = parts.index(self.repo_name)
        return ".".join(parts[repo_index + 1:-1] + (file_path.stem,))
