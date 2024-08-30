from lex_app.rest_api.model_collection.model_container import ModelContainer
from lex_app.rest_api.model_collection.utils import enrich_model_structure_with_readable_names_and_types


def _create_model_containers(models2admins):
    ids2containers = dict()

    for model_class, process_admin in models2admins.items():
        from lex.lex_app.lex_models.html_report import HTMLReport
        if not issubclass(model_class, HTMLReport):
            if model_class._meta.abstract:
                raise ValueError(
                    'The model %s is abstract, but only concrete models can be registered' % model_class._meta.model_name)
        model_container = ModelContainer(model_class, process_admin)
        ids2containers[model_container.id] = model_container

    return ids2containers


class ModelCollection:
    # TODO: Make sure that ModelCollection Instantiation works globally
    def __init__(self, models2admins, model_structure, model_styling) -> None:
        self.ids2containers = _create_model_containers(models2admins)
        self.model_structure = model_structure or {'Models': {c.id: None for c in self.all_containers}}
        self.model_styling = model_styling

        self.model_structure_with_readable_names = {
            node: enrich_model_structure_with_readable_names_and_types(node, sub_tree, self) for node, sub_tree in self.model_structure.items()
        }

    @property
    def all_containers(self):
        return set(self.ids2containers.values())

    @property
    def all_model_ids(self):
        return {c.id for c in self.all_containers}

    def get_container(self, id_or_model_class):
        return self.ids2containers[id_or_model_class]






