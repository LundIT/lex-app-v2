import os
import sys
import threading
import traceback
import asyncio
from celery import shared_task
from django.apps import AppConfig
from asgiref.sync import sync_to_async
import nest_asyncio

@shared_task(name="initial_data_upload", max_retries=0)
def load_data():
    """
    Load data asynchronously if conditions are met.
    """
    from ProcessAdminRestApi.tests.ProcessAdminTestCase import ProcessAdminTestCase
    from generic_app.models import auth_settings

    if should_load_data(auth_settings):
        try:
            test = ProcessAdminTestCase()
            test.test_path = auth_settings.initial_data_load
            print("All models are empty: Starting Initial Data Fill")
            if os.getenv("STORAGE_TYPE", "LEGACY") == "LEGACY":
                asyncio.run(sync_to_async(test.setUp)())
            else:
                if os.getenv("CELERY_ACTIVE"):
                    test.setUpCloudStorage()
                else:
                    asyncio.run(sync_to_async(test.setUpCloudStorage)())
            print("Initial Data Fill completed Successfully")
        except Exception:
            print("Initial Data Fill aborted with Exception:")
            traceback.print_exc()


def should_load_data(auth_settings):
    """
    Check whether the initial data should be loaded.
    """
    return hasattr(auth_settings, 'initial_data_load') and auth_settings.initial_data_load


class GenericAppConfig(AppConfig):
    name = 'generic_app'

    def ready(self):
        nest_asyncio.apply()
        asyncio.run(self.async_ready())

    async def async_ready(self):
        """
        Check conditions and decide whether to load data asynchronously.
        """
        from ProcessAdminRestApi.tests.ProcessAdminTestCase import ProcessAdminTestCase
        from generic_app.models import auth_settings

        if (not running_in_uvicorn()
                or os.getenv("CELERY_ACTIVE")
                or not auth_settings
                or not auth_settings.initial_data_load):
            return

        if await are_all_models_empty(auth_settings):
            if (os.getenv("DEPLOYMENT_ENVIRONMENT")
                    and os.getenv("ARCHITECTURE") == "MQ/Worker"):
                load_data.delay()
            else:
                x = threading.Thread(target=load_data)
                x.start()
        else:
            test = ProcessAdminTestCase()
            test.test_path = auth_settings.initial_data_load
            non_empty_models = await sync_to_async(test.get_list_of_non_empty_models)()
            print(f"Loading Initial Data not triggered due to existence of objects of Model: {non_empty_models}")
            print("Not all referenced Models are empty")


async def are_all_models_empty(auth_settings):
    """
    Check if all models are empty.
    """
    from ProcessAdminRestApi.tests.ProcessAdminTestCase import ProcessAdminTestCase

    test = ProcessAdminTestCase()
    test.test_path = auth_settings.initial_data_load
    return await sync_to_async(test.check_if_all_models_are_empty)()


def running_in_uvicorn():
    """
    Check if the application is running in Uvicorn context.
    """
    return sys.argv[-1:] == ["run_dpag.py"]