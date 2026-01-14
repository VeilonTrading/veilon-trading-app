from veilon_core.db import execute_query

def get_trades_by_account_id(account_id: str) -> list[dict]:
    return execute_query(
        """
        SELECT 
            *
        FROM trades
        WHERE account_id = %s
        ORDER BY open_time ASC;
        """,
        (account_id,),
    ) or []
