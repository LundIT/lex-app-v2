from django.db.models import Model

from lex_app.lex_models.Process import Process
from lex_app.lex_models.html_report import HTMLReport
from lex_app.rest_api.model_collection.constants import RELATION_FIELD_TYPES

# TODO: 2
def get_relation_fields(model: Model):
    """Get relation fields of a model."""
    return [field for field in model._meta.get_fields() if
            field.get_internal_type() in RELATION_FIELD_TYPES and not field.one_to_many]

def title_for_model(model: Model) -> str:
    """Get the title for a model."""
    return model._meta.verbose_name.title()

def get_readable_name_for(node_name, model_collection):
    if node_name in model_collection.model_styling:
        print(model_collection.model_styling)
        return model_collection.model_styling[node_name]['name']
    elif node_name in model_collection.all_model_ids:
        return model_collection.get_container(node_name).title
    return node_name


def enrich_model_structure_with_readable_names_and_types(node_name, model_tree, model_collection):
    readable_name = get_readable_name_for(node_name, model_collection)
    if not model_tree:
        model_class = model_collection.get_container(node_name).model_class
        type = "HTMLReport" if HTMLReport in model_class.__bases__ else "Process" if Process in model_class.__bases__ else "Model"
        return {'readable_name': readable_name, 'type': type}
    return {'readable_name': readable_name, 'type': "Folder", 'children': {
        sub_node: enrich_model_structure_with_readable_names_and_types(sub_node, sub_tree, model_collection) for
        sub_node, sub_tree in model_tree.items()}}
