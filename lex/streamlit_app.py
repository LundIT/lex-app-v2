import os
import streamlit as st

from streamlit_keycloak import login
import traceback
import base64
from urllib.parse import urlencode
from PIL import Image

LUND_LOGO = Image.open(f"{os.getenv('LEX_APP_PACKAGE_ROOT')}/assets/lex-logo.png")
LUND_BG = f"{os.getenv('LEX_APP_PACKAGE_ROOT')}/assets/lex-bg.jpg"


# Helper Functions
def set_bg(file):
    main_bg_ext = "png"

    st.markdown(
        f"""
         <style>
             .stApp {{
                 background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(file, "rb").read()).decode()});
                 background-size: cover;
             }}
         </style>
         """,
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    from lex_app.auth_helpers import resolve_user
    from lex_app.settings import repo_name

    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'id_token' not in st.session_state:
        st.session_state.id_token = None

    try:
        exec(f"import {repo_name}._streamlit_structure as streamlit_structure")
        st.set_page_config(layout="wide")

        keycloak_endpoint = os.getenv('KEYCLOAK_URL', default='https://auth.excellence-cloud.dev')
        keycloak_client_id = os.getenv('KEYCLOAK_CLIENT_ID', default='LEX_LOCAL_ENV')
        keycloak_realm = os.getenv('KEYCLOAK_REALM', default='lex')

        auth_type = os.getenv("STREAMLIT_AUTH_TYPE", "PRIVATE")

        if auth_type == "PUBLIC":
            streamlit_structure.main(user={'name': 'Anonymous User'})
        else:
            st.markdown(
                """
                <style>
                    div[data-testid="column"] {
                        height: 60vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] *
                    {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                    }

                    div[data-testid="column"]:nth-of-type(2) [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] 
                    { 
                        background: white; box-shadow: rgba(149, 157, 165, 0.08) 0px 8px 24px; padding: 2rem 
                    } 
                    div[data-testid="column"]:nth-of-type(2) a {
                        display: none !important;
                    }
                    button[data-testid="StyledFullScreenButton"] {
                        display: none !important;
                    }
            </style>
                """, unsafe_allow_html=True
            )

            if st.session_state.get("user_info"):
                params = urlencode(
                    {"post_logout_redirect_uri": f"{os.getenv('STREAMLIT_URL', 'http://localhost:8501')}?embed=true",
                     "id_token_hint": st.session_state.id_token, })
                footer_html = f"""
                        <div style='position: fixed; bottom: 12px; right: 12px; z-index: 100000000; font-size: 15px; background: rgb(240, 242, 246); padding: 10px 13px; border-radius: 13px;'>
                        <span> © 2024 LEX by Lund IT &nbsp; | &nbsp; </span><b><a target="_self" href="{keycloak_endpoint}/realms/{keycloak_realm}/protocol/openid-connect/logout?{params}">Logout</a></b>
                        </div>
                        """
                st.markdown(footer_html, unsafe_allow_html=True)

            if not st.session_state.authenticated:
                container = st.empty()  # Create an empty container that can be cleared later

                with container.container():
                    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
                    set_bg(f'{os.getenv("PROJECT_ROOT")}/{streamlit_structure.LOGIN_BACKGROUND}' if hasattr(
                        streamlit_structure, "LOGIN_BACKGROUND") else LUND_BG)
                    with col2:
                        with st.container(border=True):
                            st.image(f'{os.getenv("PROJECT_ROOT")}/{streamlit_structure.LOGIN_LOGO}' if hasattr(
                                streamlit_structure, "LOGIN_LOGO") else LUND_LOGO)
                            st.markdown(
                                f'<h3>{streamlit_structure.LOGIN_TITLE if hasattr(streamlit_structure, "LOGIN_TITLE") else "Welcome to the Dashboard"}</h3>',
                                unsafe_allow_html=True)
                            # st.title(streamlit_structure.LOGIN_TITLE if hasattr(streamlit_structure, "LOGIN_TITLE") else "Welcome to the Dashboard")
                            st.write(streamlit_structure.LOGIN_TEXT if hasattr(streamlit_structure,
                                                                               "LOGIN_TEXT") else "Transforming finance one byte at a time...")
                            keycloak = login(
                                url=os.getenv("KEYCLOAK_URL", "https://auth.excellence-cloud.dev"),
                                realm=os.getenv("KEYCLOAK_REALM", "lex"),
                                client_id=os.getenv("STREAMLIT_KEYCLOAK_CLIENT_ID", "LEX_LOCAL_ENV"),
                                auto_refresh=False,
                                init_options={
                                    "checkLoginIframe": False
                                },
                            )

                if keycloak.authenticated:
                    user = resolve_user(request=None, id_token=keycloak.user_info, rbac=(auth_type == "PRIVATE"))
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_info = keycloak.user_info
                        st.session_state.id_token = keycloak.id_token
                        container.empty()  # Clear the container after authentication
                        streamlit_structure.main(user=keycloak.user_info)

                    else:
                        st.error("You are not authorized to use this app.")
            else:
                streamlit_structure.main(user=st.session_state.user_info)

    except Exception as e:
        if os.getenv("DEPLOYMENT_ENVIRONMENT") != "PROD":
            raise e
        else:
            with st.expander(":red[An error occurred while trying to load the app.]"):
                st.error(traceback.format_exc())
