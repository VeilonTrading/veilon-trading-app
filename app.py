import streamlit as st
from pages.auth import render_login_screen, is_logged_in
from pages.routes import PAGES

def main():
    st.set_page_config(
        layout="centered",
        menu_items={
            "Get Help": "https://www.veilontrading.com/help",
            "Report a bug": "mailto:bug@veilontrading.com",
        },
    )

    # --- Auth gate ---
    if not is_logged_in():
        render_login_screen()
        st.stop()   # hard stop, don't render dashboard

    nav = st.navigation(pages=PAGES, position="sidebar")
    nav.run()

    st.logo("static/images/type_logo_light.png", size="large")

if __name__ == "__main__":
    main()
