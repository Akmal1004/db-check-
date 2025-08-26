# ==============================================================================
# FASTAPI ENDPOINT FOR NEXT-DAY WATCHLIST SCRAPER (v2 - Robust Error Handling)
# ==============================================================================
#
# INSTRUCTIONS:
# 1. Copy the code from this file (imports, helper function, and the endpoint).
# 2. Paste it into your main FastAPI application file, replacing the previous version.
# 3. VERIFY THE IMPORT PATHS to make sure they match your project structure.
#
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORTS
# Please verify these import paths match your project structure.
# ------------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from scraper import run_nextday_watchlist_scraper

# --- VERIFY THIS PATH ---
# You need to import your ScreenerLogRepository. The path below is a placeholder.
# from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.management.screener_log_repo import ScreenerLogRepository
# Assuming you have a ScreenerLogRepository, otherwise this will fail. For now, let's create a placeholder to avoid errors.
class ScreenerLogRepository:
    def __init__(self, session):
        self.session = session
    def start_log(self, process_name):
        print(f"INFO: (Placeholder) Starting log for {process_name}")
        class LogEntry:
            log_id = 1
        return LogEntry()
    def complete_log(self, log_id, status, error_message=None):
        print(f"INFO: (Placeholder) Completing log for {log_id} with status {status} and error: {error_message}")

# --- VERIFY THIS PATH ---
from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.management.database_manager import get_db_session
from algo_scripts.algotrade.scripts.trade_utils.trade_logger import get_trade_actions_dynamic_logger
from algo_scripts.algotrade.scripts.trade_utils.time_manager import get_current_ist_time_as_str

# ------------------------------------------------------------------------------
# 2. HELPER FUNCTION
# If you don't have this function, you can add it to your utils file and import it,
# or just include it directly in your FastAPI file.
# ------------------------------------------------------------------------------
def get_screener_logger_name(prefix, screener_name):
    """Creates a standardized logger name."""
    return f"{prefix}{screener_name}"


# ------------------------------------------------------------------------------
# 3. FASTAPI ENDPOINT (v2 - Robust Error Handling)
# Add this to your FastAPI `app` object.
# ------------------------------------------------------------------------------
# @app.get("/watchlist/trigger_nextday_scraper", tags=["Watchlist Scrapers"])
async def trigger_nextday_watchlist_scraper():
    """
    Triggers the Next-Day Watchlist scraper to log in, download the latest
    watchlist CSV, and save the contents to the database.
    """
    logger_prefix = "scraper_run_"
    screener_name = "nextday_watchlist"
    process_logger_name = get_screener_logger_name(logger_prefix, screener_name)
    logger = get_trade_actions_dynamic_logger(process_logger_name)

    session = None
    repo = None
    log_entry = None

    try:
        session = next(get_db_session())
        repo = ScreenerLogRepository(session)
        log_entry = repo.start_log(process_logger_name)

        logger.info(f"'{screener_name}' scraper process started at {get_current_ist_time_as_str()}")

        run_nextday_watchlist_scraper()

        logger.info(f"'{screener_name}' scraper process completed at {get_current_ist_time_as_str()}")
        repo.complete_log(log_entry.log_id, status="COMPLETED")
        return {"status": f"'{screener_name}' scraper completed successfully."}

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(f"A critical error occurred in '{screener_name}' scraper endpoint: {e}", exc_info=True)

        if repo and log_entry:
            repo.complete_log(log_entry.log_id, status="FAILED", error_message=error_message)

        raise HTTPException(status_code=500, detail=f"Internal Server Error in '{screener_name}' scraper. Error: {error_message}")
    finally:
        if session:
            session.close()
