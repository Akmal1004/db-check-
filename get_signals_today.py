import logging
from dotenv import load_dotenv
from sg_signals_repo import SgSignalsRepository

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to load environment variables, fetch signals, and print them.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create an instance of the repository
    try:
        repo = SgSignalsRepository()
    except ValueError as e:
        logging.error(e)
        return

    # Define the stock and trade type to query
    stock_name = "TCS"
    trade_type = "BUY"

    logging.info(f"Fetching signals for {stock_name} ({trade_type})...")

    # Get signals using the repository
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
