import os

from django.shortcuts import render

# Create your views here.
import posixpath
from pathlib import Path

from django.utils._os import safe_join
from django.views.static import serve as static_serve
from lex.lex_app import settings
from django.http import HttpResponse

def serve_react(request, path, document_root=None):
    path = posixpath.normpath(path).lstrip("/")

    if path == "config.js":
        config_path = safe_join(document_root, path)
        with open(config_path, 'r') as file:
            content = file.read()

        # Replace placeholders with actual environment variable values
        replacements = {
            'undefined': {  # Only replace 'undefined' entries
                'REACT_APP_KEYCLOAK_REALM': os.getenv('KEYCLOAK_REALM'),
                'REACT_APP_KEYCLOAK_URL': os.getenv('KEYCLOAK_URL'),
                'REACT_APP_KEYCLOAK_CLIENT_ID': os.getenv('KEYCLOAK_CLIENT_ID'),
                'REACT_APP_STORAGE_TYPE': os.getenv('STORAGE_TYPE', "LEGACY"),  # Defaults to "SHAREPOINT" if not set
                'REACT_APP_DOMAIN_BASE': os.getenv("REACT_APP_DOMAIN_BASE", "localhost"),
                'REACT_APP_PROJECT_DISPLAY_NAME': os.getenv('PROJECT_DISPLAY_NAME', settings.repo_name),
                'REACT_APP_GRAFANA_DASHBOARD_URL': os.getenv("REACT_APP_GRAFANA_DASHBOARD_URL", "localhost"),
            }
        }

        # Dynamically replace 'undefined' with actual values in the script
        for key, value in replacements['undefined'].items():
            content = content.replace(f"window.{key} = undefined", f"window.{key} = \"{value}\"")

        return HttpResponse(content, content_type='application/javascript')

    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_file():
        return static_serve(request, path, document_root)
    else:
        return static_serve(request, "index.html", document_root)