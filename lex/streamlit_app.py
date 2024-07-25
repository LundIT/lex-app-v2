import os
import streamlit as st

from streamlit_keycloak import login
import traceback

if __name__ == '__main__':
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
                user = resolve_user(request=None, id_token=keycloak.user_info, rbac=(auth_type == "PRIVATE"))
                if user:
                    streamlit_structure.main(user=keycloak.user_info)
                else:
                    st.error("You are not authorized to use this app.")

    except Exception as e:
        if os.getenv("DEPLOYMENT_ENVIRONMENT") != "PROD":
            raise e
        else:
            with st.expander(":red[An error occurred while trying to load the app.]"):
                st.error(traceback.format_exc())
