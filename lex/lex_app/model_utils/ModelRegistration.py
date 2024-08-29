from typing import Dict, Type, List

import asyncio
import nest_asyncio
from asgiref.sync import sync_to_async
import os


class ModelRegistration:

    @classmethod
    def register_models(cls, models):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite
        from lex.lex_app.lex_models.Process import Process
        from lex.lex_app.lex_models.html_report import HTMLReport

        for model in models:
            if issubclass(model, HTMLReport):
                processAdminSite.registerHTMLReport(model.__name__.lower(), model)
                processAdminSite.register([model])
            elif issubclass(model, Process):
                processAdminSite.registerProcess(model.__name__.lower(), model)
                processAdminSite.register([model])
            elif not issubclass(model, type) and not model._meta.abstract:
                processAdminSite.register([model])
                adminSite.register([model])

                from lex.lex_app.lex_models.upload_model import UploadModelMixin, ConditionalUpdateMixin
                if issubclass(model, ConditionalUpdateMixin):
                    if os.getenv("CALLED_FROM_START_COMMAND"):
                        @sync_to_async
                        def reset_instances_with_aborted_calculations():
                            if not os.getenv("CELERY_ACTIVE"):
                                aborted_calc_instances = model.objects.filter(calculate=True)
                                aborted_calc_instances.update(calculate=False)

                        nest_asyncio.apply()
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(reset_instances_with_aborted_calculations())

    @classmethod
    def register_model_structure(cls, structure: dict):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite
        if structure: processAdminSite.register_model_structure(structure)

    @classmethod
    def register_model_styling(cls, styling: dict):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite
        if styling: processAdminSite.register_model_styling(styling)

    @classmethod
    def register_global_filter_structure(cls, filter_structure: dict):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite
        if filter_structure: processAdminSite.register_global_filter_structure(filter_structure)

    @classmethod
    def register_widget_structure(cls, structure):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite
        if structure: processAdminSite.register_widget_structure(structure)