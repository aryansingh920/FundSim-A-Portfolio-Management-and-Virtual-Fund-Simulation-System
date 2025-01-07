"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/currency/model.py
"""


from sqlalchemy import (
    Column, String, Integer, DECIMAL, DateTime, Date, ForeignKey, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Basic Currency Information


class Currency(Base):
    __tablename__ = "currencies"

    # ISO 4217 currency code (e.g., USD, EUR)
    iso_code = Column(String(3), primary_key=True)
    # Full name of the currency (e.g., "US Dollar")
    name = Column(String(255), nullable=False)
    # Symbol for the currency (e.g., $, €)
    symbol = Column(String(10), nullable=False)
    # Country or region associated with the currency
    country = Column(String(255))
    # Type of currency (e.g., Fiat, Cryptocurrency)
    type = Column(String(50), nullable=False)
    # Total market capitalization (if applicable)
    market_cap = Column(DECIMAL(20, 2))

    # Historical Data Range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationships
    exchange_rates = relationship(
        "ExchangeRate", back_populates="currency", cascade="all, delete-orphan"
    )
    fundamental_metrics = relationship(
        "CurrencyFundamentals", back_populates="currency", cascade="all, delete-orphan"
    )
    volatility_risk = relationship(
        "CurrencyVolatility", back_populates="currency", cascade="all, delete-orphan"
    )
    intraday_data = relationship(
        "IntradayCurrencyData", back_populates="currency", cascade="all, delete-orphan"
    )
    market_sentiment = relationship(
        "CurrencyMarketSentiment", back_populates="currency", cascade="all, delete-orphan"
    )


# Table 2: Historical Exchange Rates
class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iso_code = Column(String(3), ForeignKey("currencies.iso_code"))
    # Base currency (e.g., USD, EUR)
    base_currency = Column(String(3), nullable=False)
    date = Column(Date, nullable=False)  # Date of the exchange rate
    # Exchange rate (against base currency)
    rate = Column(DECIMAL(20, 6), nullable=False)

    # Additional Information
    adjusted_rate = Column(DECIMAL(20, 6))  # Inflation-adjusted exchange rate
    # % change from the previous day
    daily_change_percentage = Column(DECIMAL(10, 2))
    # Volume of trades involving this currency pair
    trading_volume = Column(BigInteger)

    # Relationship back to Currency
    currency = relationship("Currency", back_populates="exchange_rates")


# Table 3: Fundamental Metrics for Currencies
class CurrencyFundamentals(Base):
    __tablename__ = "currency_fundamentals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iso_code = Column(String(3), ForeignKey("currencies.iso_code"))
    inflation_rate = Column(DECIMAL(5, 2))  # Annual inflation rate
    interest_rate = Column(DECIMAL(5, 2))  # Central bank interest rate
    # GDP growth rate of the associated country/region
    gdp_growth_rate = Column(DECIMAL(5, 2))
    # Debt-to-GDP ratio of the associated country
    debt_to_gdp_ratio = Column(DECIMAL(10, 2))
    purchasing_power_parity = Column(
        DECIMAL(20, 6))  # PPP-adjusted exchange rate

    # Historical Data Range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship back to Currency
    currency = relationship("Currency", back_populates="fundamental_metrics")


# Table 4: Volatility and Risk Metrics
class CurrencyVolatility(Base):
    __tablename__ = "currency_volatility"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iso_code = Column(String(3), ForeignKey("currencies.iso_code"))
    # Volatility measure (e.g., std dev of daily returns)
    standard_deviation = Column(DECIMAL(10, 6))
    beta = Column(DECIMAL(10, 6))  # Beta against a currency index
    # Value at Risk (VaR) at 95% confidence
    value_at_risk = Column(DECIMAL(20, 6))

    # Historical Data Range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship back to Currency
    currency = relationship("Currency", back_populates="volatility_risk")


# Table 5: Intraday Data for Currencies
class IntradayCurrencyData(Base):
    __tablename__ = "intraday_currency_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iso_code = Column(String(3), ForeignKey("currencies.iso_code"))
    date = Column(Date, nullable=False)
    timestamp = Column(DateTime, nullable=False)  # Exact timestamp of the data
    # Exchange rate or price at the given time
    price = Column(DECIMAL(20, 6), nullable=False)
    # Volume of trades in the given interval
    volume = Column(BigInteger, nullable=False, default=0)

    # Relationship back to Currency
    currency = relationship("Currency", back_populates="intraday_data")


# Table 6: Market Sentiment and Indicators
class CurrencyMarketSentiment(Base):
    __tablename__ = "currency_market_sentiment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iso_code = Column(String(3), ForeignKey("currencies.iso_code"))
    sentiment_score = Column(DECIMAL(5, 2))  # Sentiment score (-1 to 1)
    # Number of relevant news headlines
    news_headlines_count = Column(Integer, default=0)
    # Number of social media mentions
    social_media_mentions = Column(Integer, default=0)
    # Analyst's assessment (e.g., Strong Buy, Sell)
    analyst_rating = Column(String(50))

    # Historical Data Range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship back to Currency
    currency = relationship("Currency", back_populates="market_sentiment")
