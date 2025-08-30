import pytz
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Date, Index,DateTime, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from dateutil import parser
from typing import Union, Dict

from algo_scripts.algotrade.scripts.trading_style.intraday.core.intra_utils.db.management.database_manager import (
    get_db_session,
    Base,
    engine,
)

load_dotenv()

IST = pytz.timezone("Asia/Kolkata")

def now_ist():
    return datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(IST)

def today_ist() -> date:
    return now_ist().date()

# Define the OHL model
class SgOhlSignals(Base):
    __tablename__ = "sg_ohl_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screener_run_id = Column(String(50), nullable=True)
    screener_date = Column(Date, nullable=False, default=today_ist)
    screener_type = Column(String(50), nullable=True)
    screener = Column(String(50), nullable=False)
    stock_name = Column(String(50), nullable=False)
    trade_type = Column(String(50), nullable=False)
    screener_rank = Column(Integer, nullable=True)
    price = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    momentum = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    deviation_from_pivots = Column(String(50), nullable=False)
    todays_range = Column(String(50), nullable=False)
    ohl = Column(String(20), nullable=False)
    stock_type = Column(String(10), nullable=False)
    weekly_trend = Column(String(50), nullable=True)
    sector = Column(String(1000), nullable=True)  # ✅ New Column
    bullish_milestone_tags = Column(String(2500), nullable=True)  # ✅ New Column
    bearish_milestone_tags = Column(String(2500), nullable=True)  # ✅ New Column
    last_updated_time = Column(DateTime, default=now_ist, onupdate=now_ist, nullable=False)

    __table_args__ = (
        Index(
            "unique_stock_entry",
            "screener",
            "screener_date",
            "stock_name",
            "trade_type",
            "stock_type",
            unique=True,
        ),
    )

class SgOhlSignalsRepository:
    def __init__(self):
        self.session: Session = next(get_db_session())

    def insert(self, data: list):
        try:
            entry = SgOhlSignals(
                screener_run_id=data[0],
                screener_date=data[1] if data[1] else today_ist(),
                screener_type=data[2],
                screener=data[3],
                stock_name=data[4],
                trade_type=data[5],
                screener_rank=data[6],
                price=data[7],
                change=data[8],
                percentage=data[9],
                momentum=data[10],
                open=data[11],
                deviation_from_pivots=data[12],
                todays_range=data[13],
                ohl=data[14],
                stock_type=data[15],
                weekly_trend=data[16] if len(data) > 16 else None,
                sector=data[17] if len(data) > 17 else None,
                bullish_milestone_tags=data[18] if len(data) > 18 else None,
                bearish_milestone_tags=data[19] if len(data) > 19 else None,
            )
            self.session.add(entry)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print("Error inserting data:", e)

    def get_data(self, date: str | None = None):
        try:
            query = self.session.query(SgOhlSignals)
            if date:
                from datetime import datetime as _dt
                date_obj = _dt.strptime(date, "%Y-%m-%d").date()
                query = query.filter(SgOhlSignals.screener_date == date_obj)
            result = query.all()
            return [
                [
                    row.screener_run_id,
                    row.screener_date,
                    row.screener_type,
                    row.screener,
                    row.stock_name,
                    row.trade_type,
                    row.screener_rank,
                    row.price,
                    row.change,
                    row.percentage,
                    row.momentum,
                    row.open,
                    row.deviation_from_pivots,
                    row.todays_range,
                    row.ohl,
                    row.stock_type,
                    row.weekly_trend,
                    row.sector,
                    row.bullish_milestone_tags,
                    row.bearish_milestone_tags,
                ]
                for row in result
            ]
        except Exception as e:
            print("Error retrieving data:", e)
            return []

    def get_by_screener_date_and_screener(self, screener_date: str | date, screener: str):
        try:
            if isinstance(screener_date, str):
                from datetime import datetime as _dt
                date_obj = _dt.strptime(screener_date, "%Y-%m-%d").date()
            else:
                date_obj = screener_date
            result = (
                self.session.query(SgOhlSignals)
                .filter(
                    SgOhlSignals.screener_date == date_obj,
                    SgOhlSignals.screener == screener,
                    )
                .all()
            )
            return [
                [
                    row.screener_run_id,
                    row.screener_date,
                    row.screener_type,
                    row.screener,
                    row.stock_name,
                    row.trade_type,
                    row.screener_rank,
                    row.price,
                    row.change,
                    row.percentage,
                    row.momentum,
                    row.open,
                    row.deviation_from_pivots,
                    row.todays_range,
                    row.ohl,
                    row.stock_type,
                    row.weekly_trend,
                    row.sector,
                    row.bullish_milestone_tags,
                    row.bearish_milestone_tags,
                ]
                for row in result
            ]
        except Exception as e:
            print("Error retrieving data by screener_date and screener:", e)
            return []

    def update_weekly_trend(
            self,
            screener_date: str | date,
            screener: str,
            stock_name: str,
            weekly_trend: str,
    ):
        try:
            if isinstance(screener_date, str):
                from datetime import datetime as _dt
                date_obj = _dt.strptime(screener_date, "%Y-%m-%d").date()
            else:
                date_obj = screener_date
            (
                self.session.query(SgOhlSignals)
                .filter(
                    SgOhlSignals.screener_date == date_obj,
                    SgOhlSignals.screener == screener,
                    SgOhlSignals.stock_name == stock_name,
                    )
                .update({"weekly_trend": weekly_trend})
            )
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print("Error updating weekly_trend:", e)

    def delete_by_date_and_type(
            self,
            screener_date: Union[date, str],
            screener_type: str
    ) -> int:
        """
        Delete all SgIntradayScreenerSignals for the given date and screener_type.
        Returns the number of rows deleted.
        """
        # normalize date
        if isinstance(screener_date, str):
            screener_date = parser.parse(screener_date).date()

        try:
            deleted_count = (
                self.session
                .query(SgOhlSignals)
                .filter(
                    SgOhlSignals.screener_date == screener_date,
                    SgOhlSignals.screener_type == screener_type
                )
                .delete(synchronize_session='fetch')
            )
            self.session.commit()
            print(f"🗑️ Deleted {deleted_count} records for date={screener_date} and type={screener_type}")
            return deleted_count

        except Exception as e:
            print("❌ Error deleting records:", e)
            self.session.rollback()
            return 0

    def get_screener_ranks(
            self,
            screener_date: Union[date, str],
            stock_name: str
    ) -> Dict[str, int]:
        """
        Return a dict mapping each screener name to its screener_rank
        for the given date and stock.
        """
        # normalize date
        if isinstance(screener_date, str):
            screener_date = parser.parse(screener_date).date()

        # normalize stock_name
        stock_name = stock_name.strip().upper()

        rows = (
            self.session
            .query(
                SgOhlSignals.screener,
                SgOhlSignals.screener_rank
            )
            .filter(
                SgOhlSignals.screener_date == screener_date,
                SgOhlSignals.stock_name == stock_name
            )
            .all()
        )

        # build dict: { "OHL_BREAKOUT": 1, ... }
        return { screener: rank for screener, rank in rows }

    def get_signals_by_proc(self, stock_name: str, trade_type: str):
        """
        Calls the stored procedure `get_signals_today` and fetches the results.

        Args:
            stock_name: The name of the stock.
            trade_type: The type of trade (e.g., 'BUY', 'SELL').

        Returns:
            A tuple containing the list of rows and the total number of signals today.
        """
        try:
            # The session is already available as self.session
            trans = self.session.begin_nested() if self.session.in_transaction() else self.session.begin()

            # Define the stored procedure call
            proc_call = text("CALL get_signals_today(:p_name, :p_trade_type, @total_today)")

            # Execute the stored procedure
            result_proxy = self.session.execute(
                proc_call,
                {"p_name": stock_name, "p_trade_type": trade_type}
            )

            # The result of the CALL statement itself is the first result set.
            rows = result_proxy.fetchall()

            # To get the OUT parameter, we need to execute another query
            out_param_query = text("SELECT @total_today")
            total_today_result = self.session.execute(out_param_query).scalar()

            # Commit the transaction
            trans.commit()

            return rows, total_today_result
        except Exception as e:
            # Rollback in case of error
            if 'trans' in locals() and trans.is_active:
                trans.rollback()
            print(f"An error occurred: {e}")
            return [], 0
        finally:
            # The session is managed by the get_db_session generator, so we don't close it here.
            pass


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    repo = SgOhlSignalsRepository()

    sample_data = [
        "run_001",            # 0: screener_run_id
        today_ist(),           # 1: screener_date
        "OHL",                # 2: screener_type
        "OHL_BREAKOUT",      # 3: screener
        "TCS",                # 4: stock_name
        "BUY",                # 5: trade_type
        1,                     # 6: screener_rank
        3300.0,                # 7: price
        50.0,                  # 8: change
        1.5,                   # 9: percentage
        500.0,                 #10: momentum
        3200.0,                #11: open
        "S1",                 #12: deviation_from_pivots
        "3200-3400",          #13: todays_range
        "O=H",                #14: ohl
        "CASH",               #15: stock_type
        "UPWARD",             #16: weekly_trend
        "BANKING",            #17: sector
        "tag1,tag2",          #18: bullish_milestone_tags
        "tag3,tag4",          #19: bearish_milestone_tags
    ]
    repo.insert(sample_data)
    print("Inserted data successfully.")

    data = repo.get_data()
    print("Retrieved Data:", data)

    # === sample test for get_screener_ranks ===
    test_date = "2025-08-07"
    test_stock = "RELAXO"

    ranks = repo.get_screener_ranks(test_date, test_stock)
    if ranks:
        print(f"Screener ranks for {test_stock} on {test_date}:")
        for screener, rank in ranks.items():
            print(f"  • {screener}: {rank}")
    else:
        print(f"No records found for {test_stock} on {test_date}")
