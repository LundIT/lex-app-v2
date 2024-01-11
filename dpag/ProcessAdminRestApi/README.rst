===============
process_admin
===============

ProcessAdminRestApi is a Django-framework containing a Rest-API, that can be used
together with the ProcessAdminClient in order to build a database application,
which is - similar to the Django-admin - a generic CRUD-app, but more process-oriented.
That is, it generates a logical site structure out of the given set of models
and allows generating data by custom functions.

To build such a web app, this framework has to be installed and the desired models have to be registered
as described in the following.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "ProcessAdminRestApi" and "rest_framework" to your INSTALLED_APPS setting in settings.py like this::

    INSTALLED_APPS = [
        ...
        'ProcessAdminRestApi',
        'rest_framework'
    ]

2. Add CorsMiddleware to your MIDDLEWARE setting settings.py like this::

    MIDDLEWARE = [
        ...
        'corsheaders.middleware.CorsMiddleware'
    ]

3. Specify your JWT-setting in settings.py, e.g. like this::

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    }

4. Add the URL of your frontend server to the CORS-origin-list::

    CORS_ORIGIN_WHITELIST = ["http://localhost:3000"]

5. Specify the REST_FRAMEWORK setting in your settings.py::

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
        "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",)
    }

6. Subclass ProcessAdminSite and define the custom configurations

7. Create an instance processAdminSite of that subclass

8. Include the urls of the instance in your project urls.py like this::

    path('', processAdminSite.urls)

