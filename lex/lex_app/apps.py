import os
import sys
import threading
import traceback
import asyncio
from celery import shared_task
from django.apps import apps
from lex_app.settings import repo_name
from asgiref.sync import sync_to_async
import nest_asyncio

from lex_app.utils import GenericAppConfig


@shared_task(name="initial_data_upload", max_retries=0)
def load_data(test, generic_app_models):
    """
    Load data asynchronously if conditions are met.
    """
    from lex.lex_app.models import auth_settings

    if should_load_data(auth_settings):
        try:
            test.test_path = auth_settings.initial_data_load
            print("All models are empty: Starting Initial Data Fill")
            if os.getenv("STORAGE_TYPE", "LEGACY") == "LEGACY":
                asyncio.run(sync_to_async(test.setUp)())
            else:
                if os.getenv("CELERY_ACTIVE"):
                    test.setUpCloudStorage(generic_app_models)
                else:
                    asyncio.run(sync_to_async(test.setUpCloudStorage)(generic_app_models))
            print("Initial Data Fill completed Successfully")
        except Exception:
            print("Initial Data Fill aborted with Exception:")
            traceback.print_exc()


def should_load_data(auth_settings):
    """
    Check whether the initial data should be loaded.
    """
    return hasattr(auth_settings, 'initial_data_load') and auth_settings.initial_data_load


class LexAppConfig(GenericAppConfig):
    name = 'lex_app'

    def ready(self):
        super().ready()
        generic_app_models = {f"{model.__name__}": model for model in
                              set(list(apps.get_app_config(repo_name).models.values())
                                  + list(apps.get_app_config(repo_name).models.values()))}
        nest_asyncio.apply()
        asyncio.run(self.async_ready(generic_app_models))

    async def async_ready(self, generic_app_models):
        """
        Check conditions and decide whether to load data asynchronously.
        """
        from lex.lex_app.tests.ProcessAdminTestCase import ProcessAdminTestCase
        from lex.lex_app.models import auth_settings

        test = ProcessAdminTestCase()

        if (not running_in_uvicorn()
                or os.getenv("CELERY_ACTIVE")
                or not auth_settings
                or not hasattr(auth_settings, 'initial_data_load')
                or not auth_settings.initial_data_load):
            return

        if await are_all_models_empty(test, auth_settings, generic_app_models):
            if (os.getenv("DEPLOYMENT_ENVIRONMENT")
                    and os.getenv("ARCHITECTURE") == "MQ/Worker"):
                load_data.delay(test, generic_app_models)
            else:
                x = threading.Thread(target=load_data, args=(test, generic_app_models,))
                x.start()
        else:
            test.test_path = auth_settings.initial_data_load
            non_empty_models = await sync_to_async(test.get_list_of_non_empty_models)(generic_app_models)
            print(f"Loading Initial Data not triggered due to existence of objects of Model: {non_empty_models}")
            print("Not all referenced Models are empty")


async def are_all_models_empty(test, auth_settings, generic_app_models):
    """
    Check if all models are empty.
    """
    test.test_path = auth_settings.initial_data_load
    return await sync_to_async(test.check_if_all_models_are_empty)(generic_app_models)


def running_in_uvicorn():
    """
    Check if the application is running in Uvicorn context.
    """
    return sys.argv[-1:] == ["lex_app.asgi:application"] and os.getenv("CALLED_FROM_START_COMMAND")