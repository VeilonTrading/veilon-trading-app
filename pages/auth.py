import streamlit as st
from streamlit_extras.stylable_container import stylable_container

def is_logged_in() -> bool:
    """Wrapper around st.user / st.session_state, depending on how auth is configured."""
    user = getattr(st, "user", None)
    logged = getattr(user, "is_logged_in", None)
    if isinstance(logged, bool):
        return logged
    if isinstance(user, dict):
        return bool(user.get("is_logged_in", False))
    return False


def google_login_button():
    with stylable_container(
        key="google_signin_container",
        css_styles=r"""
            button {
                background-color: #ffffff;
                color: #000000;
                text-decoration: none;
                text-align: center;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                padding: 8px 16px;
                border-radius: 20px;
                border: 1px solid #dadce0;

                /* Google logo as background icon */
                background-image: url("https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA");
                background-repeat: no-repeat;
                background-position: 12px center;  /* left padding for icon */
                background-size: 26px 26px;        /* fixed icon size */

                /* make room for the icon so text doesn't overlap */
                padding-left: 52px;
            }
        """,
    ):
        st.button(
            "Sign in with Google",
            key="google_login_button",
            type="primary",
            use_container_width=False,
            on_click=st.login,
        )

def render_login_screen() -> None:
    st.set_page_config(
        page_title="Login",
        page_icon=":material/login:"
    )
    with st.container(border=False, horizontal=True):
        st.space("stretch")
        with st.container(border=False, horizontal_alignment="center"):
            st.image(image="static/images/veilon_dark.png")
            with st.container(border=False, horizontal_alignment="center", width=200):
                google_login_button()
        st.space("stretch")
