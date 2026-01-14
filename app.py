import streamlit as st
from pages.auth import render_login_screen, is_logged_in  # we'll split this out
from pages import dashboard, new_account
from pages.routes import PAGES
from pathlib import Path


def load_css():
    css_path = Path("static/css/app.css")
    st.markdown(
        f"<style>{css_path.read_text()}</style>",
        unsafe_allow_html=True,
    )

load_css()


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

    nav = st.navigation(pages=PAGES, position="hidden")
    nav.run()

if __name__ == "__main__":
    main()
