# ==============================================================================
# FASTAPI ENDPOINT FOR NEXT-DAY WATCHLIST LOADER
# ==============================================================================
#
# INSTRUCTIONS:
# 1. Copy the `nextday_watchlist_loader_action` function below.
# 2. Paste it into your main FastAPI application file with your other routes.
# 3. Ensure you have the necessary imports at the top of your file.
#
# ==============================================================================

# ------------------------------------------------------------------------------
# REQUIRED IMPORTS (ensure these are in your main FastAPI file)
# ------------------------------------------------------------------------------
# from fastapi import FastAPI, HTTPException
# from scraper import run_nextday_watchlist_scraper
# from your_logging_repo import ScreenerLogRepository, get_db_session
# from your_utils import get_screener_logger_name, get_trade_actions_dynamic_logger, get_current_ist_time_as_str

# ------------------------------------------------------------------------------
# FASTAPI ENDPOINT
# ------------------------------------------------------------------------------
# @app.get("/watchlist/nextday/loader/", tags=["Watchlist Loaders"])
async def nextday_watchlist_loader_action():
    """
    Triggers the Next-Day Watchlist scraper, logs the process,
    and handles success or failure, following the standard loader pattern.
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
