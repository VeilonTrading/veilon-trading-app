# routes.py
import streamlit as st

DASHBOARD_PAGE = st.Page("pages/dashboard.py", title="Dashboard")
CHECKOUT_PAGE  = st.Page("pages/new_account.py",  title="New Account")

PAGES = [DASHBOARD_PAGE, CHECKOUT_PAGE]