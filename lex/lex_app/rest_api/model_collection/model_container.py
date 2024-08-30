from typing import Dict, Set, Optional
from django.db.models import Model
from .constants import RELATION_FIELD_TYPES, MANY_TO_MANY_NAME
from .utils import get_relation_fields, title_for_model
from lex.lex_app.lex_models.ModelModificationRestriction import ModelModificationRestriction
from lex.lex_app.rest_api.serializers import model2serializer


class ModelContainer:
    def __init__(self, model_class: Model, process_admin) -> None:
        self.model_class = model_class
        self.process_admin = process_admin
        self.dependent_model_containers: Set['ModelContainer'] = set()
        self.obj_serializer = model2serializer(self.model_class, self.process_admin.get_fields_in_table_view(
            self.model_class)) if hasattr(model_class, '_meta') else None

    @property
    def id(self) -> str:
        return self.model_class._meta.model_name if hasattr(self.model_class,
                                                            '_meta') else self.model_class.__name__.lower()

    @property
    def title(self) -> str:
        return title_for_model(self.model_class) if hasattr(self.model_class, '_meta') else self.model_class.__name__

    @property
    def pk_name(self) -> Optional[str]:
        return self.model_class._meta.pk.name if hasattr(self.model_class, '_meta') else None

    def get_modification_restriction(self) -> ModelModificationRestriction:
        return getattr(self.model_class, 'modification_restriction', ModelModificationRestriction())

    def get_general_modification_restrictions_for_user(self, user) -> Dict[str, bool]:
        restriction = self.get_modification_restriction()
        return {
            'can_read_in_general': restriction.can_read_in_general(user, None),
            'can_modify_in_general': restriction.can_modify_in_general(user, None),
            'can_create_in_general': restriction.can_create_in_general(user, None),
            'can_delete_in_general': restriction.can_delete_in_general(user, None)
        }
