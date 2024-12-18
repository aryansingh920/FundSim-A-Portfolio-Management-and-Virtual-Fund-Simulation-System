from sqlalchemy import create_engine
from model import Base, Stock, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators

DATABASE_FILE = "data/stocks.db"


def setup_database():
    # Create a database connection
    engine = create_engine(f"sqlite:///{DATABASE_FILE}")
    Base.metadata.create_all(engine)  # Create tables based on models
    return engine


def clear_database(session):
    # Delete all records from all tables
    session.query(MarketIndicators).delete()
    session.query(VolatilityRisk).delete()
    session.query(FundamentalMetrics).delete()
    session.query(PriceTradingInfo).delete()
    session.query(Stock).delete()
    session.commit()
    print("All existing records have been deleted.")


def save_random_stock_data(session, stock_data):
    # Unpack the generated stock data
    stock, price_info, fundamentals, risk_metrics, market_indicators = stock_data

    # Explicitly add and commit each object to the session
    session.add(stock)
    session.flush()  # Ensure `stock` is saved and `ticker` is available for foreign keys

    # Associate the child objects with the parent (stock)
    price_info.ticker = stock.ticker
    session.add(price_info)

    fundamentals.ticker = stock.ticker
    session.add(fundamentals)

    risk_metrics.ticker = stock.ticker
    session.add(risk_metrics)

    market_indicators.ticker = stock.ticker
    session.add(market_indicators)

    # Commit all objects
    session.commit()
    print(f"Stock '{stock.ticker}' and related data successfully added.")
