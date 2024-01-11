import os
import sys

from pathlib import Path
import streamlit as st

import django
from streamlit_keycloak import login

app_name = 'generic_app'
PROJECT_ROOT_DIR = Path(os.path.abspath(__file__))
DJANGO_ROOT_DIR = PROJECT_ROOT_DIR
files = list(Path(__file__).resolve().parent.glob("./generic_app/submodels/**/_streamlit_structure.py"))

# Add the project base directory to the sys.path
sys.path.append(DJANGO_ROOT_DIR.as_posix())

# The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "DjangoProcessAdminGeneric.settings"
)

# This is for setting up django
django.setup()


if __name__ == '__main__':
    import sys
    from DjangoProcessAdminGeneric.auth_helpers import resolve_user
    if len(files) > 0:
        file = files[0]
        subfolders = '.'.join(file.parts[file.parts.index('submodels') + 1:-1])
        exec(f"import {app_name}.submodels.{subfolders}._streamlit_structure as streamlit_structure")
        st.set_page_config(layout="wide")
        keycloak = login(
            url=os.getenv("KEYCLOAK_URL", "https://auth.test-excellence-cloud.de"),
            realm=os.getenv("KEYCLOAK_REALM", "lex"),
            client_id=os.getenv("KEYCLOAK_CLIENT_ID", "LEX_LOCAL_ENV"),
            auto_refresh=False,
            init_options={
                "checkLoginIframe": False
            }
        )

        if keycloak.authenticated:
            user = resolve_user(request=None, id_token=keycloak.user_info)
            if user:
                streamlit_structure.main(user=keycloak.user_info)
            else:
                st.error("You are not authorized to use this app.")
