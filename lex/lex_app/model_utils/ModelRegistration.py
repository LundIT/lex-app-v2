from typing import Dict, Type, List
from django.db import models
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
            else:
                processAdminSite.register([model])
                adminSite.register([model])

    @classmethod
    def register_model_structure(cls, structure: dict):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite
        # from lex.lex_app.logging.UserChangeLog import UserChangeLog
        # from lex.lex_app.logging.CalculationLog import CalculationLog
        # from lex.lex_app.logging.CalculationIDs import CalculationIDs
        # from lex.lex_app.logging.Log import Log
        # from lex.lex_app.streamlit.Streamlit import Streamlit
        # from django.contrib.auth.models import User, Group, Permission
        # from django.contrib.contenttypes.models import ContentType

        print(structure)
        # built_in_models = [Streamlit]
        # cls.register_models(built_in_models)
        # processAdminSite.register([<Streamlit])

        # processAdminSite.registerHTMLReport("streamlit", Streamlit)
        # model_structure = shorten_model_structure(structure)

        # structure['Z_Reports'] = {'userchangelog': None, 'calculationlog': None, 'log': None}
        # if os.getenv("IS_STREAMLIT_ENABLED") == "true":
        #     structure['Streamlit'] = {'streamlit': None}

        processAdminSite.register_model_structure(structure)

    @classmethod
    def register_model_styling(cls, styling: dict):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite

        processAdminSite.register_model_styling(styling)

    @classmethod
    def register_global_filter_structure(cls, filter_structure: dict):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite

        processAdminSite.register_global_filter_structure(filter_structure)

    @classmethod
    def register_widget_structure(cls, structure):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite

        processAdminSite.register_widget_structure(structure)