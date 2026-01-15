import streamlit as st
from pages.routes import CHECKOUT_PAGE
from veilon_core.users import get_user_by_email, get_or_create_user_from_oidc
from veilon_core.accounts import get_active_accounts_for_user
from veilon_core.trades import get_trades_by_account_id
from veilon_core.db import execute_query


GLASS_TILE_CSS = """
<style>
/* Glassmorphic stat tile */
div.st-key-{key} {{
    background: rgba(23, 23, 23, 0.55) !important;
    border: 1px solid #3c3c3c !important;
    border-radius: 8px;
    padding: 16px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}}
</style>
"""

# Small HTML helpers to stop repeating giant inline strings
def _p(text: str, pb: str = "0.5rem", color: str = "var(--text-color)") -> str:
    return f"""
    <div style="
        font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
        color: {color};
        font-size: 0.875rem;
        line-height: normal;
        max-width: 100%;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        margin: 0;
        padding: 0;
    ">
        <p style="
            margin: 0;
            padding: 0;
            padding-bottom: {pb};
            overflow: hidden;
            text-overflow: ellipsis;
        ">{text}</p>
    </div>
    """

def _big_value(value: str, size: str = "1.5rem") -> str:
    return f"""
    <div style="
        font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
        color: var(--text-color);
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        line-height: normal;
        vertical-align: bottom;
    ">
        <div style="
            font-size: {size};
            font-weight: 400;
            padding-top: 0rem;
            padding-bottom: 0.5rem;
            padding-right: 0;
            line-height: 1.2;
        ">{value}</div>
    </div>
    """

def _suffix(text: str) -> str:
    return f"""
    <div style="
        font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
        color: gray;
        font-size: 0.875rem;
        line-height: normal;
        max-width: 100%;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        margin: 0;
        padding: 0;
        vertical-align: bottom;
    ">
        <p style="
            margin: 0;
            padding: 0;
            padding-bottom: 0.65rem;
            overflow: hidden;
            text-overflow: ellipsis;
        ">{text}</p>
    </div>
    """

# --------------------------------------------------------------------------------------
# UI pieces
# --------------------------------------------------------------------------------------

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
            width=168,
        )

        if st.button("", width=40, type="secondary", icon=":material/add_circle:"):
            st.switch_page(CHECKOUT_PAGE)

        with st.container(border=False, horizontal=True, horizontal_alignment="right"):
            st.button(
                "",
                key="logout-button",
                type="secondary",
                icon=":material/logout:",
                width=40,
                on_click=logout_dialog,
            )
    return selection

def render_stat_tile(
    *,
    key: str,
    title: str,
    value: str,
    value_size: str = "1.5rem",
    badge_text: str | None = None,
    badge_color: str = "green",
    right_label: str | None = None,
    progress: float | None = None,
    title_badge_text: str | None = None,
    title_badge_color: str = "green",
    height: int = 130,
    title_padding_bottom: str = "1rem",
):
    # Inject per-tile CSS once (keeps your current "st-key-..." targeting)
    st.markdown(GLASS_TILE_CSS.format(key=key), unsafe_allow_html=True)

    with st.container(key=key, border=False, height=height):
        with st.container(border=False, horizontal=True, vertical_alignment="center"):
            st.markdown(_p(title, pb=title_padding_bottom), unsafe_allow_html=True)
            if title_badge_text:
                st.badge(title_badge_text, color=title_badge_color)

        if badge_text and not title_badge_text:
            # Keep behaviour similar to your first tile (badge below big value)
            pass

        if right_label is None and progress is None:
            # Simple tile layout (like your first tile)
            st.markdown(_big_value(value, size=value_size), unsafe_allow_html=True)
            if badge_text:
                st.badge(badge_text, color=badge_color)
            return

        # Metric + right suffix + progress layout (like your tiles 2/3)
        with st.container(border=False, horizontal=True, vertical_alignment="bottom"):
            st.markdown(_big_value(value, size=value_size), unsafe_allow_html=True)
            st.space("stretch")
            if right_label:
                st.markdown(_suffix(right_label), unsafe_allow_html=True, text_alignment="right")

        if progress is not None:
            st.progress(progress)

# --------------------------------------------------------------------------------------
# Data access (tighten the surface area)
# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------------------

def dashboard_page():
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
            render_stat_tile(
                key="stat-1-tile",
                title="10k 1-Step Challenge",
                value="#21",
                value_size="1.85rem",
                badge_text="Active",
                badge_color="green",
                title_padding_bottom="0.5rem",
            )

        with col2:
            render_stat_tile(
                key="stat-2-tile",
                title="Max Drawdown",
                value="$1,000.00",
                title_badge_text="On Track",
                title_badge_color="green",
                right_label="of $10,000",
                progress=0.2,
                title_padding_bottom="1rem",
            )

        with col3:
            render_stat_tile(
                key="stat-3-tile",
                title="Profit Target",
                value="$1,000.00",
                title_badge_text="On Track",
                title_badge_color="green",
                right_label="of $10,000",
                progress=0.2,
                title_padding_bottom="1rem",
            )

        # You still have `trades` here for tables/charts
        # st.write(trades)

    with rewards_tab:
        st.caption("Rewards")

    with settings_tab:
        st.caption("Settings")

if __name__ == "__main__":
    dashboard_page()
