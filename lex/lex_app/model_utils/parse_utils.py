from typing import List, Dict, Any, Optional
import yaml

class ModelNode:
    def __init__(self, name: str, children: Optional[List['ModelNode']] = None):
        self.name = name
        self.children = children or []

    def add_child(self, child: 'ModelNode'):
        self.children.append(child)

    def find(self, name: str) -> Optional['ModelNode']:
        """Recursively find a node by name."""
        if self.name == name:
            return self
        for child in self.children:
            found = child.find(name)
            if found:
                return found
        return None

    def to_dict(self) -> Dict[str, Any]:
        return self._to_dict()

    def _to_dict(self) -> Dict[str, Any]:
        return {child.name: child._to_dict() for child in self.children}

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> List['ModelNode']:
        if data is None:
            return []
        return [ModelNode(item[0], ModelNode._from_dict(item[1])) for item in data.items() if item is not None]

    @staticmethod
    def from_yaml_file(file_path: str) -> 'ModelNode':
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return ModelNode.from_dict(data)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ModelNode':
        return ModelNode("Root", ModelNode._from_dict(data))

    @classmethod
    def to_yaml_file(cls, file_path: str, d: Dict[str, Any]):
        with open(file_path, 'w') as f:
            yaml.safe_dump(d, f)

    def __repr__(self):
        return f"ModelNode(name='{self.name}', children={len(self.children)})"

    # Example Utility Methods
    def print_tree(self, level: int = 0):
        indent = ' ' * (level * 2)
        print(f"{indent}{self.name}")
        for child in self.children:
            child.print_tree(level + 1)

    def get_all_nodes(self) -> List[str]:
        nodes = [self.name]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes
