import streamlit as st
import pandas as pd
from pages.footer import render_footer
import static.elements.charts as charts
import static.elements.metrics as metrics
import static.elements.layout as layouts
from pages.routes import CHECKOUT_PAGE
from veilon_core.users import get_user_by_email, get_or_create_user_from_oidc
from veilon_core.accounts import get_active_accounts_for_user
from veilon_core.trades import get_trades_by_account_id
from veilon_core.db import execute_query

performance_data = pd.DataFrame({
    "Date": [
        "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04",
        "2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08",
        "2024-01-09", "2024-01-10", "2024-01-11", "2024-01-12",
        "2024-01-13", "2024-01-14"
    ],
    "Balance": [
        100000, 100400, 100900, 101300,
        100800, 101700, 102600, 103200,
        103900, 104500, 105300, 105900,
        106700, 107400
    ],
    "Equity": [
        100000, 100600, 101200, 101800,
        101100, 102200, 103100, 103800,
        104400, 105000, 105900, 106500,
        107300, 108000
    ],
    "Profit Target": [
        110000, 110000, 110000, 110000,
        110000, 110000, 110000, 110000,
        110000, 110000, 110000, 110000,
        110000, 110000
    ],
    "Max Drawdown": [
        90000, 90000, 90000, 90000,
        90000, 90000, 90000, 90000,
        90000, 90000, 90000, 90000,
        90000, 90000
    ],
    "Daily Drawdown": [
        95000, 95400, 95900, 96300,
        95800, 96700, 97600, 98200,
        98900, 99500, 100300, 100900,
        101700, 102400
    ]
})

daily_return_data = pd.DataFrame({
    "Date": [
        "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04",
        "2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08",
        "2024-01-09", "2024-01-10", "2024-01-11", "2024-01-12",
        "2024-01-13", "2024-01-14"
    ],
    "Gain": [
        0, 0.004, 0.005, 0.004, -0.005, 0.009, 0.009, 0.006,
        0.007, 0.006, 0.008, 0.006, 0.008, 0.007
    ],
})

veilon_score = 46
account_type = "$50k Assessment"
account_status = "Active"
return_stat = "1.10%"
daily_dradwown_stat = "0.00%"
max_drawdown_stat = "4.10%"


def render_add_account_modal():
    with st.popover(
        label="Add Account",
        width=162,
        type="secondary",
        icon=":material/add:",
    ):
        account_name_input = st.text_input(
            label="Account Name",
            help="Custom Name, e.g. Account 1",
        )
        account_login_input = st.text_input(
            label="Login",
            help="Account Number/Login",
        )
        account_password_input = st.text_input(
            label="Investor Password",
            type="password",
            help='Your read-only "Investor Password"',
        )
        account_platform_input = st.selectbox(
            label="Platform",
            options=["MetaTrader 4", "MetaTrader 5"],
        )
        st.button("Connect", use_container_width=True)


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


def render_header():
    with st.container(border=False, horizontal=True, vertical_alignment="center"):
        # Left: welcome text
        with st.container(
            border=False,
            horizontal=True,
            horizontal_alignment="left",
            vertical_alignment="center",
        ):
            st.subheader(f"Welcome, {st.user.given_name}", anchor=False)

        # Right: logo
        with st.container(
            border=False,
            horizontal=True,
            horizontal_alignment="right",
            vertical_alignment="center",
        ):
            with st.container(border=False, width=200, vertical_alignment="center"):
                st.image("static/images/veilon_dark.png")


def get_user_and_accounts():
    """
    Resolve current user via Google / OIDC.
    If they don't exist yet in `users`, create a minimal user row.
    Then fetch their active accounts.
    """
    # Raw claims from st.user
    email = st.user.email.strip().lower()
    given_name = getattr(st.user, "given_name", None)
    family_name = getattr(st.user, "family_name", None)

    user = get_or_create_user_from_oidc(
        email=email,
        given_name=given_name,
        family_name=family_name,
    )
    user_id = user["id"]

    user_accounts = get_active_accounts_for_user(user_id)
    return user_id, user_accounts


def get_account_trades(account_id):
    return get_trades_by_account_id(account_id)


def build_account_options(user_accounts):
    """
    Build account_map, account_options, and disabled flag from DB rows.
    """
    if user_accounts:
        account_map = {
            f"{account['id']}": account["id"]
            for account in user_accounts
        }
        account_options = list(account_map.keys())
        select_disabled = False
    else:
        account_map = {}
        account_options = ["No accounts available"]
        select_disabled = True

    return account_map, account_options, select_disabled


def render_account_selector(account_options, select_disabled):
    """
    Render the account selectbox + add-account + logout controls.
    Returns the selected label string (same as original behaviour).
    """
    with st.container(
        border=False,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
    ):
        account_selection = st.selectbox(
            label="Select Account",
            options=account_options,
            disabled=select_disabled,
            width=286,
        )

        if st.button(
            label="",
            width=40,
            type="secondary",
            icon=":material/add:",
        ):
            st.switch_page(CHECKOUT_PAGE)

        with st.container(border=False, horizontal=True, horizontal_alignment="right"):
            st.button(
                label="",
                key="logout-button",
                width=40,
                type="secondary",
                icon=":material/logout:",
                on_click=logout_dialog,
            )

    return account_selection


def render_overview_tab(trades):
    with st.container(
        border=False,
        horizontal=True,
        horizontal_alignment="center"
    ):
        metrics.gradient_metric_tile(
            key="account-status",
            stat=account_type,
            value=account_status,
            tooltip="",
        )

        metrics.standard_metric_tile(
            key="return",
            stat="Return",
            value=return_stat,
            tooltip="",
        )

        metrics.standard_metric_tile(
            key="daily-drawdown-tile",
            stat="Daily Drawdown",
            value=daily_dradwown_stat,
            tooltip="",
        )

        metrics.standard_metric_tile(
            key="dmax-drawdown-tile",
            stat="Max Drawdown",
            value=max_drawdown_stat,
            tooltip="",
        )

    with layouts.tile(key="overview-chart", height=300, border=True):
        st.caption("Performance")

        performance_data["Date"] = pd.to_datetime(performance_data["Date"])
        chart = charts.performance_chart(performance_data)
        st.altair_chart(chart, width="stretch")

    with st.container(border=False, horizontal=True):
        with layouts.tile(key="bar-chart", height=300, border=True):
            st.caption("Daily Return")
            chart = charts.daily_return_chart(daily_return_data)
            st.altair_chart(chart, width="stretch")

        with st.container(border=False, width=163):
            with layouts.tile(key="tile-1", height=300, border=True):
                st.caption(
                    "Veilon Score",
                    help=(
                        "The Trader Score represents a blended rating based on five key performance pillars:\n\n"
                        "• History Quality: depth and reliability of the trader’s track record\n\n"
                        "• Profitability: consistency of returns over time\n\n"
                        "• Consistency: stability of performance and variance control\n\n"
                        "• Risk Management: drawdown control and position sizing discipline\n\n"
                        "• Behaviour: adherence to rules, discipline, and emotional stability\n\n"
                        "A score of 100 indicates perfect performance across all five pillars."
                    ),
                )
                chart = charts.veilon_score_bar(veilon_score)
                st.altair_chart(chart, width="stretch")


def render_rewards_tab():
    with st.container(
        border=False,
        horizontal=True,
        horizontal_alignment="center"
    ):
        metrics.gradient_metric_tile(
            key="withdrawable_profit",
            stat="Total Profit",
            value="$0.00",
            tooltip="",
        )

        metrics.standard_metric_tile(
            key="reward_countdown",
            stat="Next Reward Date",
            value="21st Nov",
            tooltip="",
        )

        metrics.standard_metric_tile(
            key="total_withdrawals",
            stat="Total Rewards",
            value="$1,251.12",
            tooltip="",
        )

        metrics.standard_metric_tile(
            key="avg-withdrawal",
            stat="Average Reward",
            value="1",
            tooltip="",
        )

    with layouts.tile(key="payout-chart", height=300, border=True):
        st.caption("Reward History")

    with st.container(
        border=False,
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="bottom",
    ):
        with layouts.tile(key="withdraw-request", height=150, border=True):
            st.caption("New Request")
            with st.container(
                border=False,
                horizontal=True,
                horizontal_alignment="left",
                vertical_alignment="bottom",
            ):
                with st.container(width=200):
                    st.number_input("Amount", 0, 5000)
                st.button("Request")

        with layouts.tile(key="withdraw-request-log", height=150, border=True):
            st.caption("Request Status")


def render_settings_tab():
    st.empty()


def dashboard_page():
    render_header()

    user_id, user_accounts = get_user_and_accounts()

    account_map, account_options, select_disabled = build_account_options(user_accounts)

    account_selection = render_account_selector(account_options, select_disabled)

    selected_account_id = account_map.get(account_selection)

    if not selected_account_id:
        trades = []
    else:
        trades = get_account_trades(selected_account_id)

    if len(user_accounts) == 0:
        st.info("Add an account to see your performance data, metrics and trade history.")
    else:
        overview_tab, rewards_tab, settings_tab = st.tabs(
            ["Overview", "Rewards", "Settings"])

        with overview_tab:
            render_overview_tab(trades)

        with rewards_tab:
            render_rewards_tab()

        with settings_tab:
            render_settings_tab()

    render_footer()


if __name__ == "__main__":
    dashboard_page()
