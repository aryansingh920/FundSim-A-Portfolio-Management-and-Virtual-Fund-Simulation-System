"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/etf/model.py
"""

from sqlalchemy import (
    Column, String, Integer, DECIMAL, ForeignKey, Date, DateTime, Text, BigInteger, Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Basic ETF Information


class ETF(Base):
    __tablename__ = "etfs"

    # Unique identifier for the ETF
    etf_id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)  # Full name of the ETF
    ticker = Column(String(10), unique=True,
                    nullable=False)  # ETF ticker symbol
    # E.g., Equity, Bond, Commodity, Real Estate
    category = Column(String(100))
    strategy = Column(String(100))  # Passive, Active, Thematic
    issuer = Column(String(255))  # Issuer of the ETF
    inception_date = Column(Date, nullable=False)  # ETF inception date
    expense_ratio = Column(DECIMAL(5, 2))  # Annual expense ratio (in %)
    # Total assets under management (AUM)
    assets_under_management = Column(DECIMAL(20, 2))
    # Currency of trading (e.g., USD, EUR)
    trading_currency = Column(String(10), nullable=False)
    is_leveraged = Column(Integer, default=0)  # 1 if leveraged, 0 otherwise
    is_inverse = Column(Integer, default=0)  # 1 if inverse, 0 otherwise

    # Relationships
    underlying_assets = relationship(
        "ETFUnderlyingAsset", back_populates="etf", cascade="all, delete-orphan"
    )
    performance_metrics = relationship(
        "ETFPerformanceMetrics", back_populates="etf", cascade="all, delete-orphan"
    )
    historical_data = relationship(
        "ETFHistoricalData", back_populates="etf", cascade="all, delete-orphan"
    )
    market_indicators = relationship(
        "ETFMarketIndicators", back_populates="etf", cascade="all, delete-orphan"
    )

# Table 2: Underlying Assets


class ETFUnderlyingAsset(Base):
    __tablename__ = "etf_underlying_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    etf_id = Column(String(20), ForeignKey("etfs.etf_id"))
    # Type of asset (e.g., Stock, Bond, Commodity, Currency)
    asset_type = Column(String(50))
    # Identifier of the asset (e.g., ticker or ISIN)
    asset_id = Column(String(50))
    weight = Column(DECIMAL(5, 2))  # Weight of the asset in the ETF (in %)

    # Relationship
    etf = relationship("ETF", back_populates="underlying_assets")

# Table 3: Performance Metrics


class ETFPerformanceMetrics(Base):
    __tablename__ = "etf_performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    etf_id = Column(String(20), ForeignKey("etfs.etf_id"))
    # Annualized return (in %)
    annualized_return = Column(DECIMAL(5, 2))
    # Annualized volatility (in %)
    annualized_volatility = Column(DECIMAL(5, 2))
    sharpe_ratio = Column(DECIMAL(5, 2))  # Risk-adjusted return
    # Deviation from the benchmark index
    tracking_error = Column(DECIMAL(5, 2))
    dividend_yield = Column(DECIMAL(5, 2))  # Dividend yield (in %)
    beta = Column(DECIMAL(5, 2))  # Volatility relative to the market index

    # Relationship
    etf = relationship("ETF", back_populates="performance_metrics")

# Table 4: Historical Data


class ETFHistoricalData(Base):
    __tablename__ = "etf_historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    etf_id = Column(String(20), ForeignKey("etfs.etf_id"))
    date = Column(Date, nullable=False)  # Date of the historical record
    # Opening price of the ETF
    open_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))  # Closing price of the ETF
    day_high = Column(DECIMAL(10, 2))  # Highest price during the day
    day_low = Column(DECIMAL(10, 2))  # Lowest price during the day
    trading_volume = Column(BigInteger)  # Number of units traded
    # Adjusted closing price (for splits/dividends)
    adjusted_close_price = Column(DECIMAL(10, 2))

    # Relationship
    etf = relationship("ETF", back_populates="historical_data")

# Table 5: Market Indicators


class ETFMarketIndicators(Base):
    __tablename__ = "etf_market_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    etf_id = Column(String(20), ForeignKey("etfs.etf_id"))
    RSI = Column(Integer)  # Relative Strength Index
    moving_avg_50 = Column(DECIMAL(10, 2))  # 50-day moving average
    moving_avg_200 = Column(DECIMAL(10, 2))  # 200-day moving average
    MACD = Column(String(50))  # Moving Average Convergence Divergence
    analyst_rating = Column(String(50))  # Analyst rating (e.g., Buy/Hold/Sell)

    # Relationship
    etf = relationship("ETF", back_populates="market_indicators")
