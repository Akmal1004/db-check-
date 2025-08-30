import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class SgSignalsRepository:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set.")
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_signals_by_proc(self, stock_name: str, trade_type: str):
        """
        Calls the stored procedure `get_signals_today` and fetches the results.

        Args:
            stock_name: The name of the stock.
            trade_type: The type of trade (e.g., 'BUY', 'SELL').

        Returns:
            A tuple containing the list of rows and the total number of signals today.
        """
        session = self.Session()
        try:
            # Start a transaction
            trans = session.begin()

            # Define the stored procedure call
            proc_call = text("CALL get_signals_today(:p_name, :p_trade_type, @total_today)")

            # Execute the stored procedure
            result_proxy = session.execute(
                proc_call,
                {"p_name": stock_name, "p_trade_type": trade_type}
            )

            # The result of the CALL statement itself is the first result set.
            rows = result_proxy.fetchall()

            # To get the OUT parameter, we need to execute another query
            # within the same transaction.
            out_param_query = text("SELECT @total_today")
            total_today_result = session.execute(out_param_query).scalar()

            # Commit the transaction
            trans.commit()

            return rows, total_today_result
        except Exception as e:
            # Rollback in case of error
            trans.rollback()
            print(f"An error occurred: {e}")
            return [], 0
        finally:
            # Close the session
            session.close()
