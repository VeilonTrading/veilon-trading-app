import streamlit as st
from pages.routes import CHECKOUT_PAGE
from veilon_core.users import get_user_by_email, get_or_create_user_from_oidc
from veilon_core.accounts import get_active_accounts_for_user
from veilon_core.trades import get_trades_by_account_id
from veilon_core.db import execute_query
from static.elements.metrics import metric_tile, empty_tile

@st.dialog("Logout")
def logout_dialog():
    st.write("Are you sure you want to log out?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes", type="secondary", width="stretch"):
            st.logout()
    with col2:
        if st.button("No", type="secondary", width="stretch"):
            st.rerun()

def render_account_selector(account_labels: list[str], disabled: bool) -> str:
    with st.container(border=False, horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"):
        selection = st.selectbox(
            "Select Account",
            options=account_labels,
            disabled=disabled,
            width=222,
        )

        if st.button("", width=40, type="secondary", icon=":material/add_circle:"):
            st.switch_page(CHECKOUT_PAGE)
            
        st.space("stretch")

        st.button(
            "",
            key="logout-button",
            type="secondary",
            icon=":material/logout:",
            width=40,
            on_click=logout_dialog,
        )
    return selection

def get_user_id() -> int:
    email = st.user.email.strip().lower()
    user = get_or_create_user_from_oidc(
        email=email,
        given_name=getattr(st.user, "given_name", None),
        family_name=getattr(st.user, "family_name", None),
    )
    return user["id"]

def get_user_accounts(user_id: int) -> list[dict]:
    return get_active_accounts_for_user(user_id)

def build_account_label_map(accounts: list[dict]) -> tuple[dict[str, int], list[str], bool]:
    if not accounts:
        return {}, ["No accounts available"], True

    # If you later want nicer labels, change this once (e.g. f"#{id} • {name}")
    label_to_id = {str(a["id"]): a["id"] for a in accounts}
    return label_to_id, list(label_to_id.keys()), False

def dashboard_page():
    st.set_page_config(
        page_title="Dashboard",
        page_icon=":material/home:"
    )
    with st.container(border=False, horizontal=True, vertical_alignment="center"):
        with st.container(border=False, horizontal=True, horizontal_alignment="left", vertical_alignment="center"):
            st.subheader(f"Welcome, {getattr(st.user, 'given_name', '')}", anchor=False)

    user_id = get_user_id()
    accounts = get_user_accounts(user_id)

    label_to_id, labels, disabled = build_account_label_map(accounts)
    selected_label = render_account_selector(labels, disabled)
    selected_account_id = label_to_id.get(selected_label)

    trades = get_trades_by_account_id(selected_account_id) if selected_account_id else []

    if not accounts:
        st.info("Add an account to see your performance data, metrics and trade history.")
        return

    overview_tab, rewards_tab, settings_tab = st.tabs(["Overview", "Rewards", "Settings"])

    with overview_tab:
       
        col1, col2, col3 = st.columns(3)

        with col1:
            metric_tile(
                key="stat-1-tile",
                title="10k 1-Step Challenge",
                value="#21",
                value_size="1.85rem",
                footer_badge="Active",
                footer_badge_color="green",
                title_padding_bottom="0.5rem",
            )

        with col2:
            metric_tile(
                key="stat-2-tile",
                title="Max Drawdown",
                title_badge="On Track",
                title_badge_color="green",
                value="$1,000.00",
                right_label="of $10,000",
                progress=0.2,
            )

        with col3:
            metric_tile(
                key="stat-3-tile",
                title="Profit Target",
                title_badge="On Track",
                title_badge_color="green",
                value="$1,000.00",
                right_label="of $10,000",
                progress=0.2,
            )

        with empty_tile(key="performance-chart", height=300):
            st.caption("Performance Chart")

        col4, col5 = st.columns(2)

        with col4:
            with empty_tile(key="stats-tile", height=300):
                st.caption("Account Stats")

        with col5:
            with empty_tile(key="actions-tile", height=300):
                st.caption("Account Actions")
                st.button("Progress", disabled=True, type="secondary", width="stretch")     

        # You still have `trades` here for tables/charts
        # st.write(trades)

    with rewards_tab:
        st.caption("Rewards")

    with settings_tab:
        st.caption("Settings") 
    
if __name__ == "__main__":
    dashboard_page()
