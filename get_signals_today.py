import logging
from sg_ohl_signals import SgOhlSignalsRepository

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to fetch signals using the repository and print them.
    """
    # Note: The .env file is loaded by the database_manager mock.
    # In a real application, you might load it here explicitly.

    logging.info("Initializing repository...")

    try:
        # Create an instance of the repository
        # The repository will get a DB session from the mock database_manager
        repo = SgOhlSignalsRepository()
    except Exception as e:
        logging.error(f"Failed to initialize repository: {e}")
        return

    # Define the stock and trade type to query
    stock_name = "TCS"
    trade_type = "BUY"

    logging.info(f"Fetching signals for {stock_name} ({trade_type}) via stored procedure...")

    # Get signals using the new method in the repository
    rows, total_today = repo.get_signals_by_proc(stock_name, trade_type)

    # Print the results
    if total_today is not None:
        logging.info(f"📌 Found {total_today} signals for {stock_name} ({trade_type}) today")
        if rows:
            for row in rows:
                logging.info(row)
    else:
        logging.warning("Could not retrieve the total number of signals.")

if __name__ == "__main__":
    main()
