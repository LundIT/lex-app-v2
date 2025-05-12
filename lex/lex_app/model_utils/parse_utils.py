import yaml


class ModelStructure:
    def __init__(self, path: str):
        self.path = path
        self.structure = {}
        self.styling = {}

        self._load_info()

    def _load_info(self):
        with open(self.path, "r") as f:
            data = yaml.safe_load(f)
        try:
            self.structure = data["model_structure"]
        except (KeyError, TypeError):
            print("Error: Structure is not defined in the model info file")
        try:
            self.styling = data["model_styling"]
        except (KeyError, TypeError):
            print("Error: Styling is not defined in the model info file")

    def structure_is_defined(self):
        return bool(self.structure)
