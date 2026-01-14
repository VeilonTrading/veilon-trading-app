import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from pages.footer import render_footer

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

def tile(
    key,
    height,
    width,
    border,
    horizontal,
    horizontal_alignment,
    vertical_alignment,
):
    secondary_background = "#111111"
    light_text_color     = "#E8E8E8"
    border_color         = "#3c3c3c"

    border_style = f"1px solid {border_color};" if border else "none;"

    with stylable_container(
        key=key,
        css_styles=f"""
        {{
            background-color: {secondary_background};
            font-family: "Source Sans Pro", sans-serif;
            font-weight: 400;
            border-radius: 0.5rem;
            border: {border_style};
            padding: calc(1em - 1px);
            color: {light_text_color};
        }}
        """
    ):
        # inner container = where Streamlit widgets go
        return st.container(
            border=False, 
            height=height, 
            width=width, 
            horizontal=horizontal, 
            horizontal_alignment=horizontal_alignment, 
            vertical_alignment=vertical_alignment
            )

def render_login_screen() -> None:

    #st.container(border=False, height=250)
    
    with st.container(border=False, horizontal=True, height=700,horizontal_alignment="center", vertical_alignment="center"):
        with st.container(border=False, height=400, width=320, vertical_alignment="center"):
            st.image(image="static/images/veilon_dark.png")
            st.markdown(
                    """
                    <div style="text-align: center; font-size: 1.5rem; color: "#3c3c3c";>
                        Acceleration Program
                    </div>
                    """,
                    unsafe_allow_html=True
                )
           # st.write("")
           # st.markdown(
           #         """
           #         <div style="text-align: center; font-size: 1.5rem; color: "#3c3c3c";>
           #             Demonstrate your trading excellence.
           #         </div>
           #         """,
           #         unsafe_allow_html=True
           #     )
        
        with st.container(border=False, height=400, width=320, vertical_alignment="center"):
            with tile(key="auth-interface", height=370, width=300, border=False, vertical_alignment="center", horizontal=False, horizontal_alignment="distribute"):
                with st.container(border=False, horizontal=True, horizontal_alignment="center"):
                    st.markdown(
                    """
                    <div style="text-align: center; font-size: 1.5rem; color: "#3c3c3c";>
                        Sign Up
                    </div>
                    """,
                    unsafe_allow_html=True
                    )
                    
                    with st.container(border=False, width=200):
                        st.write("")
                        st.write("")
                        google_login_button()
    
        
        
