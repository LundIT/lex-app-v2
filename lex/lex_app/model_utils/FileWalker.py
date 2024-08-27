from pathlib import Path
from typing import List

class FileWalker:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def get_python_files(self) -> List[Path]:
        return [
            f for f in self.base_path.glob("./**/[!_]*.py")
            if 'venv' not in f.parts and '.venv' not in f.parts and 'build' not in f.parts
        ]

    def get_auth_settings_file(self) -> Path:
        auth_files = list(self.base_path.glob("**/_authentication_settings.py"))
        return auth_files[0] if auth_files else None
