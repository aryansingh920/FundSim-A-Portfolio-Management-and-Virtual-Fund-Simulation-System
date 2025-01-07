"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/mutualFund/model.py
"""

from sqlalchemy import (
    Column, String, Integer, DECIMAL, DateTime, Date, ForeignKey, BigInteger, Text, Enum
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Table 1: Basic Mutual Fund Information


class MutualFund(Base):
    __tablename__ = "mutual_funds"

    # Unique ID for the mutual fund
    fund_id = Column(String(20), primary_key=True)
    fund_name = Column(String(255), nullable=False)  # Name of the fund
    fund_category = Column(String(100))  # Equity, Debt, Hybrid, etc.
    fund_type = Column(Enum("Open-Ended", "Close-Ended",
                       "Interval", name="fund_type_enum"))
    inception_date = Column(Date, nullable=False)  # Date the fund was launched
    fund_manager = Column(String(255))  # Fund manager's name
    fund_company = Column(String(255))  # Asset Management Company (AMC)
    benchmark = Column(String(100))  # Fund's benchmark index (e.g., S&P 500)
    total_assets_under_management = Column(DECIMAL(20, 2))  # Total AUM in USD
    currency = Column(String(10), default="USD")  # Currency of the fund

    # Historical Data Range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationships
    portfolio = relationship(
        "MutualFundPortfolio", back_populates="fund", cascade="all, delete-orphan")
    performance_metrics = relationship(
        "MutualFundPerformance", back_populates="fund", cascade="all, delete-orphan")
    risk_metrics = relationship(
        "MutualFundRiskMetrics", back_populates="fund", cascade="all, delete-orphan")
    expense_structure = relationship(
        "MutualFundExpense", back_populates="fund", cascade="all, delete-orphan")
    sentiment = relationship(
        "MutualFundSentiment", back_populates="fund", cascade="all, delete-orphan")


# Table 2: Mutual Fund Portfolio Composition
class MutualFundPortfolio(Base):
    __tablename__ = "mutual_fund_portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to MutualFund
    fund_id = Column(String(20), ForeignKey("mutual_funds.fund_id"))
    asset_type = Column(Enum("Stock", "Bond", "Commodity",
                        "Currency", "Real Estate", name="asset_type_enum"))
    # Asset Identifier (e.g., ticker for stock, ISIN for bond)
    asset_id = Column(String(20))
    # Percentage of the portfolio allocated to this asset
    weightage = Column(DECIMAL(5, 2))

    # Relationship back to MutualFund
    fund = relationship("MutualFund", back_populates="portfolio")


# Table 3: Mutual Fund Performance Metrics
class MutualFundPerformance(Base):
    __tablename__ = "mutual_fund_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to MutualFund
    fund_id = Column(String(20), ForeignKey("mutual_funds.fund_id"))
    date = Column(Date, nullable=False)  # Date of the performance record
    nav = Column(DECIMAL(10, 2))  # Net Asset Value per unit
    one_year_return = Column(DECIMAL(5, 2))  # % return over 1 year
    three_year_return = Column(DECIMAL(5, 2))  # % return over 3 years
    five_year_return = Column(DECIMAL(5, 2))  # % return over 5 years

    # Relationship back to MutualFund
    fund = relationship("MutualFund", back_populates="performance_metrics")


# Table 4: Risk Metrics
class MutualFundRiskMetrics(Base):
    __tablename__ = "mutual_fund_risk_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to MutualFund
    fund_id = Column(String(20), ForeignKey("mutual_funds.fund_id"))
    beta = Column(DECIMAL(5, 2))  # Fund's beta compared to its benchmark
    standard_deviation = Column(DECIMAL(5, 2))  # Annualized standard deviation
    sharpe_ratio = Column(DECIMAL(5, 2))  # Risk-adjusted return
    alpha = Column(DECIMAL(5, 2))  # Excess return over the benchmark
    r_squared = Column(DECIMAL(5, 2))  # Correlation with the benchmark

    # Relationship back to MutualFund
    fund = relationship("MutualFund", back_populates="risk_metrics")


# Table 5: Expense Structure
class MutualFundExpense(Base):
    __tablename__ = "mutual_fund_expense"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to MutualFund
    fund_id = Column(String(20), ForeignKey("mutual_funds.fund_id"))
    expense_ratio = Column(DECIMAL(5, 2))  # Annual expense ratio (% of AUM)
    entry_load = Column(DECIMAL(5, 2))  # Entry load fee (%)
    exit_load = Column(DECIMAL(5, 2))  # Exit load fee (%)
    management_fee = Column(DECIMAL(5, 2))  # Management fee (% of AUM)

    # Relationship back to MutualFund
    fund = relationship("MutualFund", back_populates="expense_structure")


# Table 6: Market Sentiment and Ratings
class MutualFundSentiment(Base):
    __tablename__ = "mutual_fund_sentiment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to MutualFund
    fund_id = Column(String(20), ForeignKey("mutual_funds.fund_id"))
    sentiment_score = Column(DECIMAL(5, 2))  # Sentiment score (-1 to 1)
    # Number of relevant news headlines
    news_mentions = Column(Integer, default=0)
    # Number of social media mentions
    social_media_mentions = Column(Integer, default=0)
    # Analyst rating (e.g., Buy, Hold, Sell)
    analyst_rating = Column(String(50))

    # Relationship back to MutualFund
    fund = relationship("MutualFund", back_populates="sentiment")
