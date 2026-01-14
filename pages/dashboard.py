import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
from pages.footer import render_footer
import static.elements.charts as charts
import static.elements.metrics as metrics
import static.elements.layout as layouts
from pages.routes import CHECKOUT_PAGE
from backend.repositories.users import get_user_by_email, get_or_create_user_from_oidc
from backend.repositories.accounts import get_active_accounts_for_user
from backend.repositories.trades import get_trades_by_account_id
from backend.database import execute_query

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

        # # Right: logo
        # with st.container(
        #     border=False,
        #     horizontal=True,
        #     horizontal_alignment="right",
        #     vertical_alignment="center",
        # ):
        #     with st.container(border=False, width=200, vertical_alignment="center"):
        #         st.image("static/images/veilon_dark.png")


def get_user_id():
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

    return user_id


def get_user_accounts(user_id):
    user_accounts = get_active_accounts_for_user(user_id)

    return user_accounts


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
            width=168,
        )

        if st.button(
            label="",
            width=40,
            type="secondary",
            icon=":material/add_circle:",
        ):
            st.switch_page(CHECKOUT_PAGE)

        with st.container(border=False, horizontal=True, horizontal_alignment="right"):
            st.button(
                label="",
                key="logout-button",
                type="secondary",
                icon=":material/logout:",
                width=40,
                on_click=logout_dialog,
            )

    return account_selection


def dashboard_page():
    render_header()

    user_id = get_user_id()
    user_accounts = get_user_accounts(user_id)

    #Account info dict needed
    # Need Status for badge,
    # Account type

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
 
            col1, col2, col3 = st.columns(3)

            st.markdown(
                """
                <style>
                /* Glassmorphic stat tile */
                div.st-key-stat-1-tile {
                    background: rgba(23, 23, 23, 0.55) !important;
                    border: 1px solid #3c3c3c !important;
                    border-radius: 8px;
                    padding: 16px;

                    backdrop-filter: blur(18px);
                    -webkit-backdrop-filter: blur(18px);

                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <style>
                /* Glassmorphic stat tile */
                div.st-key-stat-2-tile {
                    background: rgba(23, 23, 23, 0.55) !important;
                    border: 1px solid #3c3c3c !important;
                    border-radius: 8px;
                    padding: 16px;

                    backdrop-filter: blur(18px);
                    -webkit-backdrop-filter: blur(18px);

                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <style>
                /* Glassmorphic stat tile */
                div.st-key-stat-3-tile {
                    background: rgba(23, 23, 23, 0.55) !important;
                    border: 1px solid #3c3c3c !important;
                    border-radius: 8px;
                    padding: 16px;

                    backdrop-filter: blur(18px);
                    -webkit-backdrop-filter: blur(18px);

                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            with col1:
               with st.container(key="stat-1-tile", border=False, height=130):
                    with st.container(border=False, horizontal=True, vertical_alignment="center"):
                        st.markdown(
                            """
                            <div style="
                                font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                                color: var(--text-color);
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
                                    padding-bottom: 0.5rem;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                ">
                                    10k 1-Step Challenge
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    st.markdown(
                        """
                        <div style="
                            font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                            color: var(--text-color);
                            width: 100%;
                            overflow: hidden;
                            white-space: nowrap;
                            text-overflow: ellipsis;
                            line-height: normal;
                            vertical-align: middle;
                        ">
                            <div style="
                                font-size: 1.85rem;
                                font-weight: 400;
                                padding-top: 0;
                                padding-bottom: 0.5rem;
                                line-height: 1.2;
                            ">
                                #21
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.badge("Active", color="green")

            with col2:
                with st.container(key="stat-2-tile", border=False, height=130):
                    with st.container(border=False, horizontal=True, vertical_alignment="center"):
                        st.markdown(
                            """
                            <div style="
                                font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                                color: var(--text-color);
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
                                    padding-bottom: 1rem;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                ">
                                    Max Drawdown
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.badge("On Track", color="green")

                    with st.container(border=False, horizontal=True, vertical_alignment="bottom"):
                        st.markdown(
                            """
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
                                    font-size: 1.5rem;
                                    font-weight: 400;
                                    padding-top: 0rem;
                                    padding-bottom: 0.5rem;
                                    padding-right: 0;
                                    line-height: 1.2;
                                ">
                                    $1,000.00
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.space("stretch")
                        st.markdown(
                                """
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
                                        padding-right: 0;
                                        padding-left: 0;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                    ">
                                        of $10,000
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                                text_alignment="right",
                            )
                    st.progress(0.2)

            with col3:
                with st.container(key="stat-3-tile", border=False, height=130):
                    with st.container(border=False, horizontal=True, vertical_alignment="center"):
                        st.markdown(
                            """
                            <div style="
                                font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                                color: var(--text-color);
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
                                    padding-bottom: 1rem;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                ">
                                    Profit Target
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.badge("On Track", color="green")

                    with st.container(border=False, horizontal=True, vertical_alignment="bottom"):
                        st.markdown(
                            """
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
                                    font-size: 1.5rem;
                                    font-weight: 400;
                                    padding-top: 0rem;
                                    padding-bottom: 0.5rem;
                                    padding-right: 0;
                                    line-height: 1.2;
                                ">
                                    $1,000.00
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.space("stretch")
                        st.markdown(
                                """
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
                                        padding-right: 0;
                                        padding-left: 0;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                    ">
                                        of $10,000
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                                text_alignment="right",
                            )
                    st.progress(0.2) 

        with rewards_tab:
            st.caption("Rewards")

        with settings_tab:
            st.caption("Settings")


if __name__ == "__main__":
    dashboard_page()
