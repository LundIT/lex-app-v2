import os
import sys

from pathlib import Path
import streamlit as st

import django
from streamlit_keycloak import login


LEX_APP_PACKAGE_ROOT = Path(__file__).resolve().parent.as_posix()
PROJECT_ROOT_DIR = Path(os.getcwd()).resolve()

sys.path.append(LEX_APP_PACKAGE_ROOT)

# The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "lex_app.settings"
)
os.environ.setdefault(
    "PROJECT_ROOT", PROJECT_ROOT_DIR.as_posix()
)

django.setup()


if __name__ == '__main__':
    import sys
    from lex_app.auth_helpers import resolve_user
    from lex_app.settings import repo_name
    try:
        exec(f"import {repo_name}._streamlit_structure as streamlit_structure")
        st.set_page_config(layout="wide")


        auth_type = os.getenv("STREAMLIT_AUTH_TYPE", "PRIVATE")

        if auth_type == "PUBLIC":
            streamlit_structure.main(user={'name': 'Anonymous User'})
        else:
            keycloak = login(
                url=os.getenv("KEYCLOAK_URL", "https://auth.excellence-cloud.dev"),
                realm=os.getenv("KEYCLOAK_REALM", "lex"),
                client_id=os.getenv("STREAMLIT_KEYCLOAK_CLIENT_ID", "LEX_LOCAL_ENV"),
                auto_refresh=False,
                init_options={
                    "checkLoginIframe": False
                }
            )

            if keycloak.authenticated:
                try:
                    user = resolve_user(request=None, id_token=keycloak.user_info, rbac=(auth_type == "PRIVATE"))
                    if user:
                        try:
                            streamlit_structure.main(user=keycloak.user_info)
                        except Exception as e:
                            if os.getenv("DEPLOYMENT_ENVIRONMENT") == "PROD":
                                st.error("An error occurred while trying to load the app. Please contact with your administrator.")
                            raise e

                    else:
                        st.error("You are not authorized to use this app.")
                except Exception as e:
                    st.error("You are not authorized to use this app.")
                    raise e

    except ImportError:
        pass