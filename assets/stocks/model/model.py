# model.py
from sqlalchemy import (
    Column, String, Integer, DECIMAL, ForeignKey, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Basic Stock Information
class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String(10), primary_key=True)  # Unique stock symbol
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    market_cap = Column(DECIMAL(20, 2))  # Total market capitalization
    cap_category = Column(String(20))  # Large-Cap, Mid-Cap, Small-Cap
    shares_outstanding = Column(BigInteger)

    # Relationships
    price_trading_info = relationship("PriceTradingInfo", back_populates="stock")
    fundamental_metrics = relationship("FundamentalMetrics", back_populates="stock")
    volatility_risk = relationship("VolatilityRisk", back_populates="stock")
    market_indicators = relationship("MarketIndicators", back_populates="stock")


# Table 2: Price and Trading Information
class PriceTradingInfo(Base):
    __tablename__ = "price_trading_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"))  # Foreign Key to stocks
    current_price = Column(DECIMAL(10, 2))
    open_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))
    day_high = Column(DECIMAL(10, 2))
    day_low = Column(DECIMAL(10, 2))
    week_52_high = Column(DECIMAL(10, 2))
    week_52_low = Column(DECIMAL(10, 2))
    trading_volume = Column(BigInteger)
    average_volume = Column(BigInteger)

    # Relationship
    stock = relationship("Stock", back_populates="price_trading_info")


# Table 3: Fundamental Metrics
class FundamentalMetrics(Base):
    __tablename__ = "fundamental_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"))  # Foreign Key to stocks
    earnings_per_share = Column(DECIMAL(10, 2))  # EPS
    price_to_earnings = Column(DECIMAL(10, 2))  # P/E Ratio
    dividend_yield = Column(DECIMAL(5, 2))
    return_on_equity = Column(DECIMAL(5, 2))  # ROE
    debt_to_equity = Column(DECIMAL(5, 2))  # D/E
    revenue_growth = Column(DECIMAL(5, 2))
    net_income = Column(DECIMAL(20, 2))

    # Relationship
    stock = relationship("Stock", back_populates="fundamental_metrics")


# Table 4: Volatility and Risk Metrics
class VolatilityRisk(Base):
    __tablename__ = "volatility_risk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"))  # Foreign Key to stocks
    beta = Column(DECIMAL(5, 2))  # Stock Volatility
    standard_deviation = Column(DECIMAL(5, 2))  # Price variation
    sharpe_ratio = Column(DECIMAL(5, 2))  # Risk-adjusted return

    # Relationship
    stock = relationship("Stock", back_populates="volatility_risk")


# Table 5: Market Sentiment and Indicators
class MarketIndicators(Base):
    __tablename__ = "market_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"))  # Foreign Key to stocks
    RSI = Column(Integer)  # Relative Strength Index
    moving_avg_50 = Column(DECIMAL(10, 2))  # 50-day moving average
    moving_avg_200 = Column(DECIMAL(10, 2))  # 200-day moving average
    MACD = Column(String(50))  # Trend-following momentum indicator
    analyst_rating = Column(String(50))  # Buy/Hold/Sell Rating

    # Relationship
    stock = relationship("Stock", back_populates="market_indicators")
