from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import pytz

# Assume the user-provided files are in this structure
# This is a placeholder for the actual import.
# If the structure is different, this will need to be adjusted.
from algo_scripts.algotrade.scripts.trading_style.intraday.get_intra_nextday_watchlist import run_nextday_watchlist_scraper
from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.screener.sg_nextday_watchlist_repo import get_db_session

app = FastAPI()

# Placeholder for logging utilities, as their location is unknown.
def get_screener_logger_name(prefix, screener_name):
    return f"{prefix}{screener_name}"

def get_trade_actions_dynamic_logger(process_logger_name):
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(process_logger_name)

def get_current_ist_time_as_str():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

# Placeholder for ScreenerLogRepository, as its location is unknown.
class ScreenerLogRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def start_log(self, process_logger_name):
        log_entry = {"log_id": 1, "name": process_logger_name}
        print(f"Starting log for {process_logger_name}")
        return type("LogEntry", (), log_entry)()

    def complete_log(self, log_id, status, error_message=None):
        print(f"Completing log for {log_id} with status {status}")
        if error_message:
            print(f"Error: {error_message}")

@app.get("/intraday/screener/Next_Day_Watchlist/loader")
async def next_day_watchlist_loader_action(db_session: Session = Depends(get_db_session)):
    logger_prefix = "load_screener_"
    screener_name = "next_day_watchlist"
    process_logger_name = get_screener_logger_name(logger_prefix, screener_name)
    logger = get_trade_actions_dynamic_logger(process_logger_name)

    repo = ScreenerLogRepository(db_session)
    log_entry = repo.start_log(process_logger_name)

    try:
        run_nextday_watchlist_scraper()
        logger.info(f"Completed Processing {screener_name} at {get_current_ist_time_as_str()}")
        repo.complete_log(log_entry.log_id, status="COMPLETED")
        return {"status": f"{screener_name} loaded successfully"}
    except Exception as e:
        repo.complete_log(log_entry.log_id, status="FAILED", error_message=str(e))
        logger.error(f"Failed Processing {screener_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{screener_name} processing failed: {str(e)}")
