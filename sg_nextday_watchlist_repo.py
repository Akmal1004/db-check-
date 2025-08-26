import os
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, select, delete
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError

# ---------------- LOAD ENV AND SETUP LOGGING ----------------
load_dotenv()
# Default to a local SQLite DB if DATABASE_URL is not set, for portability
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nextday_watchlist.db")
if not DATABASE_URL:
    raise ValueError("❌ Please set DATABASE_URL in .env file or ensure the script can create a local sqlite db.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

def now_ist():
    """Returns the current time in IST timezone."""
    return datetime.now(IST)

# ---------------- SQLALCHEMY SETUP ----------------
try:
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logger.critical(f"Failed to connect to the database: {e}")
    exit(1)


def get_db_session():
    """Provides a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- ORM TABLE ----------------
class SgNextDayWatchlist(Base):
    __tablename__ = "nextday_watchlist_info"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    symbol = Column("Symbol", String(50), nullable=False, unique=True)
    price = Column("Price", String(50))
    momentum = Column("Momentum", Text)
    vol_1d_5d = Column("1D/5D Vol", String(50))
    weekly_bo = Column("Weekly BO", String(20))
    monthly_bo = Column("Monthly BO", String(20))
    yearly_bo = Column("Yearly BO", String(20))
    oi_chg = Column("OI CHG", String(50))
    buy_level = Column("Buy Level", String(50))
    sell_level = Column("Sell Level", String(50))
    created_at = Column(String(100), default=lambda: now_ist().isoformat())

    def __repr__(self):
        return f"<SgNextDayWatchlist(symbol='{self.symbol}', price='{self.price}', created_at='{self.created_at}')>"

# ---------------- REPOSITORY ----------------
class SgNextDayWatchlistRepository:
    """
    Handles all database operations for the SgNextDayWatchlist table.
    """
    def __init__(self, db_session: Session):
        self.session = db_session

    def insert(self, record: dict):
        """Inserts a single record into the database."""
        try:
            new_record = SgNextDayWatchlist(**record)
            self.session.add(new_record)
            self.session.commit()
            logger.info(f"Successfully inserted record for {record.get('symbol')}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error inserting record for {record.get('symbol')}: {e}", exc_info=True)
            self.session.rollback()
            return False

    def bulk_insert(self, records: list[dict]):
        """Bulk inserts a list of records."""
        if not records:
            logger.info("No records to bulk insert.")
            return 0
        try:
            self.session.bulk_insert_mappings(SgNextDayWatchlist, records)
            self.session.commit()
            count = len(records)
            logger.info(f"Successfully bulk inserted {count} records.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error during bulk insert: {e}", exc_info=True)
            self.session.rollback()
            return 0

    def get_all(self, limit: int = 100):
        """Retrieves all records, up to a given limit."""
        try:
            query = select(SgNextDayWatchlist).limit(limit)
            result = self.session.execute(query).scalars().all()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all records: {e}", exc_info=True)
            return []

    def get_by_symbol(self, symbol: str):
        """Retrieves a single record by its symbol."""
        try:
            query = select(SgNextDayWatchlist).where(SgNextDayWatchlist.symbol == symbol)
            result = self.session.execute(query).scalar_one_or_none()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving record by symbol {symbol}: {e}", exc_info=True)
            return None

    def delete_by_symbol(self, symbol: str):
        """Deletes records for a given symbol."""
        try:
            stmt = delete(SgNextDayWatchlist).where(SgNextDayWatchlist.symbol == symbol)
            result = self.session.execute(stmt)
            self.session.commit()
            logger.info(f"Deleted {result.rowcount} record(s) for symbol {symbol}.")
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Error deleting record by symbol {symbol}: {e}", exc_info=True)
            self.session.rollback()
            return 0

# ---------------- MAIN BLOCK FOR DEMONSTRATION ----------------
if __name__ == "__main__":
    logger.info("Starting script execution...")

    logger.info("Creating table 'nextday_watchlist_info' if it doesn't exist...")
    Base.metadata.create_all(engine)
    logger.info("Table setup complete.")

    db_session = next(get_db_session())
    repo = SgNextDayWatchlistRepository(db_session)

    # Clean up previous test data for a fresh run
    logger.info("\n--- Cleaning up old data ---")
    repo.delete_by_symbol("RELIANCE")
    repo.delete_by_symbol("TCS")
    repo.delete_by_symbol("INFY")

    # Sample data for insertion
    sample_records = [
        {
            "symbol": "RELIANCE", "price": "2900.50", "momentum": "High", "vol_1d_5d": "1.2",
            "weekly_bo": "Yes", "monthly_bo": "No", "yearly_bo": "No", "oi_chg": "5%",
            "buy_level": "2910", "sell_level": "2890",
        },
        {
            "symbol": "TCS", "price": "3800.00", "momentum": "Medium", "vol_1d_5d": "1.0",
            "weekly_bo": "No", "monthly_bo": "Yes", "yearly_bo": "No", "oi_chg": "2%",
            "buy_level": "3810", "sell_level": "3790",
        },
    ]

    logger.info("\n--- Testing Bulk Insert ---")
    repo.bulk_insert(sample_records)

    logger.info("\n--- Testing Single Insert ---")
    repo.insert({
        "symbol": "INFY", "price": "1500.75", "momentum": "Low", "vol_1d_5d": "0.8",
        "weekly_bo": "No", "monthly_bo": "No", "yearly_bo": "Yes", "oi_chg": "-1%",
        "buy_level": "1510", "sell_level": "1490",
    })

    logger.info("\n--- Retrieving all records ---")
    all_data = repo.get_all()
    if all_data:
        for item in all_data:
            logger.info(f"  - {item}")
    else:
        logger.warning("  No data found.")

    logger.info("\n--- Retrieving record for 'TCS' ---")
    tcs_data = repo.get_by_symbol("TCS")
    if tcs_data:
        logger.info(f"  - Found: {tcs_data}")
    else:
        logger.warning("  - 'TCS' not found.")

    logger.info("\n--- Deleting record for 'RELIANCE' ---")
    repo.delete_by_symbol("RELIANCE")

    logger.info("\n--- Retrieving all records to verify deletion ---")
    all_data_after_delete = repo.get_all()
    if all_data_after_delete:
        for item in all_data_after_delete:
            logger.info(f"  - {item}")
    else:
        logger.warning("  No data found.")

    logger.info("\n--- Script execution finished ---")
