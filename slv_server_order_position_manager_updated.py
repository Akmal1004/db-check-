from fastapi import BackgroundTasks
import uuid
import requests
import traceback

from algo_scripts.algotrade.scripts.trade_utils.trade_logger import get_trade_actions_dynamic_logger
from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.management.monitor_lock import \
    MonitorPLLockRepository
from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.orders.primary_account_orders import \
    PrimaryAccountOrdersRepository
from algo_scripts.algotrade.scripts.trading_style.intraday.core.trade_processor.check_and_update_positions import \
    check_and_update_positions, monitor_pl

from algo_scripts.algotrade.logs.Login_r_totp import fyers_login_db
from algo_scripts.algotrade.scripts.trading_style.intraday.strategies.intraday_screener.scanner.get_intra_nextday_watchlist import run_nextday_watchlist_scraper

from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
from algo_scripts.algotrade.scripts.trading_style.intraday.strategies.tradingview_alerts.tradingview_alerts_intra_strategy_v1 import  place_limit_order
from algo_scripts.algotrade.scripts.trading_style.invest.core.invest_trade_processor.invest_check_and_trade_processor import check_invest_token
from algo_scripts.algotrade.scripts.trading_style.invest.core.invest_trade_processor.invest_check_and_trade_processor import check_and_trade_etf

from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.gsheets_logger import log_to_gsheets, \
    log_sell_signals_to_gsheets
from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.management.database_manager import (
    engine, get_db_session, SessionScoped, initialize_global_session, close_global_session, cleanup
)
from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.screener.sg_nextday_watchlist_repo import SgNextDayWatchlistRepository
from algo_scripts.algotrade.scripts.trade_utils.time_manager import get_current_ist_time_as_str, convert_utc_to_ist
from algo_scripts.algotrade.scripts.trade_utils.time_manager import get_today_date_as_str

from fastapi.responses import JSONResponse
import os
import atexit


from typing import Optional
import json
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import pandas as pd

from algo_scripts.algotrade.scripts.trading_style.options.core.log_utils.options_trade_logger import \
    get_fno_sell_logger_name, get_options_trade_actions_dynamic_logger

# ==============================================================================
# JULES: ADDED PLACEHOLDER FOR ScreenerLogRepository
# Please replace this with the correct import for your ScreenerLogRepository
# For example:
# from your_path.screener_log_repo import ScreenerLogRepository
# ==============================================================================
class ScreenerLogRepository:
    def __init__(self, session):
        self.session = session
        print("INFO: Using placeholder ScreenerLogRepository")
    def start_log(self, process_name):
        print(f"INFO: (Placeholder) Starting log for {process_name}")
        class LogEntry:
            log_id = 1
        return LogEntry()
    def complete_log(self, log_id, status, error_message=None):
        print(f"INFO: (Placeholder) Completing log for {log_id} with status {status} and error: {error_message}")
# ==============================================================================


load_dotenv(override=True)
SOURCE_REPO = os.getenv('SOURCE_REPO')
LOTT_SELL_URL= os.getenv('LOTT_SELL_URL')

# Basic logging configuration for fallback logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
def get_screener_logger_name(prefix, screener_name):
    """Creates a standardized logger name."""
    return f"{prefix}{screener_name}"


# Register FastAPI startup event
@app.on_event("startup")
def startup():
    """Initialize global session at startup."""
    initialize_global_session()

# Register FastAPI shutdown event
@app.on_event("shutdown")
def shutdown():
    """Cleanup database connections when the app shuts down."""
    close_global_session()
    cleanup()

# Also register cleanup in case the container is forcefully stopped
atexit.register(cleanup)

@app.get("/process_exit_positions")
async def process_exit_positions():

    logger_name = "exit_intraday_positions"
    logger = get_trade_actions_dynamic_logger(logger_name)  # Dynamic logger
    logger.info("TRIGGERED process_exit_positions  " + get_current_ist_time_as_str())

    repo = PrimaryAccountOrdersRepository()
    trade_date = get_today_date_as_str()
    active_trades = repo.get_active_orders_by_date(trade_date)
    #trade_date = "2025-02-18"
    #stock_name = "NSE:NESTLEIND-EQ" #TESTING
    #active_trades = repo.get_active_orders_by_date_and_stock(trade_date,stock_name)
    logger.info("Fetched Trades from DB at   " + get_current_ist_time_as_str() + " Count = " + str(len(active_trades)))
    check_and_update_positions(logger_name,active_trades)

@app.get("/monitor_pl")
async def monitor_pl_and_exit_positions():

    db_session = next(get_db_session())  # Get DB session
    lock_repo = MonitorPLLockRepository(db_session)

    if not lock_repo.acquire_lock():
        return {"message": "Another instance is running. Skipping execution."}

    logger_name = "monitor_pl_and_exit_positions"
    logger = get_trade_actions_dynamic_logger(logger_name)
    logger.info("TRIGGER Entry monitor_pl_and_exit_positions " + get_current_ist_time_as_str())

    try:
        monitor_pl(logger_name)
    finally:
        lock_repo.release_lock()  # Release lock
        db_session.close()  # Close session after execution

    logger.info("TRIGGER Exit monitor_pl_and_exit_positions " + get_current_ist_time_as_str())
    return {"message": "Execution completed"}

@app.get("/process_etf_buy_on_dip")
async def process_entry_triggered_bullish_stocks():
    strategy_name = "etf_buy_on_dip"
    logger = get_trade_actions_dynamic_logger(strategy_name)  # Dynamic logger

    logger.info("Starting invest_stocks processing at " + get_current_ist_time_as_str())

    check_and_trade_etf(logger)

    logger.info("Completed intra_screener_stocks processing at " + get_current_ist_time_as_str())



@app.get("/fyers/login/{username}")
async def fyers_login(username: str):
    strategy_name = "fyers_login"
    logger = get_trade_actions_dynamic_logger(strategy_name)  # Dynamic logger

    logger.info("Starting fyers_login processing at " + get_current_ist_time_as_str())


    logger.info(f"API called for username: {username}")

    if username.lower() != "rajesh":
        logger.warning(f"Unauthorized username: {username}")
        raise HTTPException(status_code=403, detail="Unauthorized username")

    try:
        # Wrap your existing function safely
        access_token = fyers_login_db(logger)
        return {"status": "success", "username": username, "access_token": access_token}
    except SystemExit:
        # Catch sys.exit() calls in your login function
        logger.error("Login process exited unexpectedly. Check credentials or DB connection.")
        raise HTTPException(status_code=500, detail="Login process exited unexpectedly. Check credentials or DB connection.")
    except Exception as e:
        logger.error(f"Unexpected error:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")

@app.get("/order_position_manager/health")
def health_check():
    return {"status": "Order_Position_Manager healthy"}

# ==============================================================================
# JULES: ADDED NEW ENDPOINT FOR NEXT-DAY WATCHLIST
# ==============================================================================
@app.get("/watchlist/nextday/loader/", tags=["Watchlist Loaders"])
async def nextday_watchlist_loader_action():
    """
    Triggers the Next-Day Watchlist scraper, logs the process,
    and handles success or failure.
    """
    logger_prefix = "load_screener_"
    screener_name = "nextday_watchlist"
    process_logger_name = get_screener_logger_name(logger_prefix, screener_name)
    logger = get_trade_actions_dynamic_logger(process_logger_name)

    session = next(get_db_session())
    repo = ScreenerLogRepository(session)
    log_entry = repo.start_log(process_logger_name)

    logger.info(f"Started Processing {screener_name} at {get_current_ist_time_as_str()}")
    try:
        # --- Execute the Next-Day Watchlist scraper function ---
        run_nextday_watchlist_scraper()

        logger.info(f"Completed Processing {screener_name} at {get_current_ist_time_as_str()}")
        repo.complete_log(log_entry.log_id, status="COMPLETED")
        return {"status": f"{screener_name} loaded successfully"}
    except Exception as e:
        repo.complete_log(log_entry.log_id, status="FAILED", error_message=str(e))
        logger.error(f"Failed Processing {screener_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{screener_name} failed: {str(e)}")
    finally:
        session.close()
# ==============================================================================

def _ff_post(payload: dict):
    """
    Fire‑and‑forget POST: send JSON payload, ignore any errors.
    """
    try:
        requests.post(LOTT_SELL_URL, json=payload, timeout=1)
    except Exception:
        pass
