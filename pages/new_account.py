import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.stylable_container import stylable_container
import static.elements.layout as layouts
from pages.routes import DASHBOARD_PAGE
from pages.footer import render_footer
from veilon_core.plans import get_plan_by_account_size
from veilon_core.coupons import get_active_coupon_by_code
from veilon_core.db import execute_query
from veilon_core.users import get_user_by_email, get_or_create_user_from_oidc

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


def test_order_process(current_user_id: int, account_size: int):
    # 1) Get plan details (id + price) from your plans table
    plan_rows = execute_query(
        f"""
        SELECT id, price
        FROM plans
        WHERE account_size = {account_size}
        LIMIT 1;
        """
    )

    if not plan_rows:
        st.error("No plan found for this account size.")
        return

    plan = plan_rows[0]
    plan_id = plan["id"]
    price = plan["price"]  # numeric(10,2) in DB

    # 2) Insert a new order, treating this as a successful 'paid' order
    order_rows = execute_query(
        f"""
        INSERT INTO orders (
            user_id,
            plan_id,
            price,
            currency,
            success,
            status,
            expiry_date
        )
        VALUES (
            {current_user_id},
            {plan_id},
            {price},
            'USD',
            TRUE,
            'paid',
            NOW() + INTERVAL '30 days'
        )
        RETURNING id;
        """
    )

    order_id = order_rows[0]["id"]

    # 3) Insert a skeleton account linked to this order
    account_rows = execute_query(
        f"""
        INSERT INTO accounts (
            metaapi_account_id,
            user_id,
            order_id,
            plan_id,
            platform,
            broker,
            server,
            leverage,
            login
        )
        VALUES (
            NULL,
            {current_user_id},
            {order_id},
            {plan_id},
            NULL,
            NULL,
            NULL,
            NULL,
            NULL
        )
        RETURNING id;
        """
    )

    account_id = account_rows[0]["id"]

    # 4) Backfill orders.account_id to link the order to this account
    execute_query(
        f"""
        UPDATE orders
        SET account_id = {account_id}
        WHERE id = {order_id};
        """
    )

    print(f"Test order created. order_id={order_id}, account_id={account_id}")


def new_account_page():
    with st.container(border=False, horizontal=True, vertical_alignment="center"):
        with st.container(
            border=False,
            horizontal=True,
            horizontal_alignment="left",
            vertical_alignment="bottom",
        ):
            if st.button(
                label="Back",
                type="tertiary",
                icon=":material/arrow_back_ios:",
            ):
                st.switch_page(DASHBOARD_PAGE)

        with st.container(
            border=False,
            horizontal=True,
            horizontal_alignment="right",
            vertical_alignment="center",
        ):
            with st.container(border=False, width=200, vertical_alignment="center"):
                st.image("static/images/veilon_dark.png")

    st.subheader("New Assessment", anchor=False)
    st.caption("Demonstrate your performance through our assessment program.")

    with st.container(border=False, horizontal=True):
        # LEFT COLUMN: info + account size
        with st.container(border=False):
            with st.container(border=True, height=568):
                st.write("**Assessment Information**")
                st.caption(
                    "The Assessment is your pathway to demonstrating professional-grade trading capability. Over a 30-day period, you will trade your own external MT4/5 account while we independently evaluate your performance against a defined set of risk and consistency metrics."
                )
                st.caption(
                    "Your trading activity is mirrored to a simulated account size of your choosing, enabling us to assess position management, discipline, and risk adherence at scale. Larger starting balances provide greater performance-based reward potential throughout the program."
                )
                st.caption(
                    "Consistent, controlled, and data-driven execution is central to securing long-term placement on the Veilon trading desk."
                )
                account_size = st.selectbox(
                    label="**Select Account Size**",
                    options=(50000, 25000, 10000, 5000)
                )

                if st.button("TEST ORDER PROCESS", width="stretch"):
                    # replace these with your real values
                    current_user_id =  get_user_id()

                    test_order_process(current_user_id, account_size)

        with st.container(border=False, width=300):
            with st.container(
                key="account-rules",
                border=True,
                height=300
            ):
                st.write("**Assessment Specifications**")

                # Fetch plan from DB based on account_size
                plan = get_plan_by_account_size(account_size)

                col1, col2 = st.columns(2, vertical_alignment="center")

                with col1:
                    st.caption("Starting Balance:")
                    st.caption("Reward Share:")
                    st.caption("Profit Target:")
                    st.caption("Daily Drawdown:")
                    st.caption("Max Drawdown:")
                    st.caption("Reset Period:")

                with col2:
                    st.caption(f"${account_size:,}")
                    st.caption("80%")
                    st.caption(f"10% (${account_size * 0.1:,.2f})")
                    st.caption(f"5% (${account_size * 0.05:,.2f})")
                    st.caption(f"10% (${account_size * 0.1:,.2f})")
                    st.caption("Monthly")
        
            payment_button_id_query = execute_query(f"SELECT buy_button_id FROM plans WHERE account_size = {account_size}")

            buy_button_id = payment_button_id_query[0]["buy_button_id"]

            with st.container(border=False):
                components.html(
                    f"""
                    <script async src="https://js.stripe.com/v3/buy-button.js"></script>

                    <stripe-buy-button
                        buy-button-id={buy_button_id}
                        publishable-key="pk_test_51SUrJdDgd8xHlmy8nQdZAlJnnBpNPi4ZnJohvHAReJWJVcDBQLMHxu3Tuj6Arbu2cFy8Se2eeYHSBrbxqqjHvmKh008MvYFyNY">
                    </stripe-buy-button>
                    """,
                    height=220,   # adjust as needed so it’s not clipped
                    scrolling=False,
                )

if __name__ == "__main__":
    new_account_page()
