"""
Created on 07/01/2025

@author: Aryan

Filename: credit_fund.py

Relative Path: src/assets/creditFund/model.py
"""

from sqlalchemy import (
    Column, String, Integer, DECIMAL, Date, Enum, Text, ForeignKey, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Credit Fund Basic Information


class CreditFund(Base):
    __tablename__ = "credit_funds"

    fund_id = Column(Integer, primary_key=True, autoincrement=True)
    fund_name = Column(String(255), nullable=False,
                       unique=True)  # Unique Fund Name
    fund_type = Column(Enum("Open-End", "Closed-End",
                       "Interval", name="fund_type_enum"))
    inception_date = Column(Date, nullable=False)  # Fund creation date
    manager = Column(String(255))  # Fund Manager Name
    management_company = Column(String(255))  # Name of the managing company
    # Investment objective (e.g., high-yield bonds, secured debt, diversified credit)
    investment_objective = Column(Text)

    # Key metrics
    # Total Assets Under Management (AUM)
    total_assets = Column(DECIMAL(20, 2))
    net_asset_value = Column(DECIMAL(20, 2))  # Fund NAV
    expense_ratio = Column(DECIMAL(5, 2))  # Annual expense ratio
    yield_to_maturity = Column(DECIMAL(5, 2))  # Average YTM of the portfolio
    # Average duration of the portfolio
    average_duration = Column(DECIMAL(5, 2))

    # Historical Data Tracking
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationships
    holdings = relationship(
        "CreditFundHoldings", back_populates="credit_fund", cascade="all, delete-orphan"
    )
    performance_metrics = relationship(
        "CreditFundPerformance", back_populates="credit_fund", cascade="all, delete-orphan"
    )


# Table 2: Credit Fund Holdings
class CreditFundHoldings(Base):
    __tablename__ = "credit_fund_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to credit_funds
    fund_id = Column(Integer, ForeignKey("credit_funds.fund_id"))
    asset_type = Column(Enum("Bond", "Loan", "Real Estate",
                        "Stock", "Cash", name="asset_type_enum"))
    # References the primary key of related asset (e.g., ISIN, ticker, property_id)
    asset_id = Column(String(255))
    # Percentage weight of the asset in the fund
    weight = Column(DECIMAL(5, 2))
    acquisition_date = Column(Date)  # Date the asset was acquired

    # Relationships
    credit_fund = relationship("CreditFund", back_populates="holdings")


# Table 3: Credit Fund Performance Metrics
class CreditFundPerformance(Base):
    __tablename__ = "credit_fund_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to credit_funds
    fund_id = Column(Integer, ForeignKey("credit_funds.fund_id"))
    date = Column(Date, nullable=False)  # Date of performance measurement
    nav = Column(DECIMAL(20, 2))  # Net Asset Value
    return_percentage = Column(DECIMAL(5, 2))  # Percentage return on the fund
    volatility = Column(DECIMAL(5, 2))  # Standard deviation of returns
    sharpe_ratio = Column(DECIMAL(5, 2))  # Risk-adjusted return
    drawdown = Column(DECIMAL(5, 2))  # Maximum drawdown (loss)

    # Relationships
    credit_fund = relationship(
        "CreditFund", back_populates="performance_metrics")


# Table 4: Credit Fund Risk Metrics
class CreditFundRiskMetrics(Base):
    __tablename__ = "credit_fund_risk_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to credit_funds
    fund_id = Column(Integer, ForeignKey("credit_funds.fund_id"))
    beta = Column(DECIMAL(5, 2))  # Sensitivity to market movements
    credit_risk = Column(DECIMAL(5, 2))  # Risk of default of fund holdings
    liquidity_risk = Column(DECIMAL(5, 2))  # Risk due to illiquid holdings
    interest_rate_risk = Column(DECIMAL(5, 2))  # Risk due to rate fluctuations
    # Correlation with stock markets
    correlation_with_equities = Column(DECIMAL(5, 2))

    # Relationships
    credit_fund = relationship("CreditFund")


# Table 5: Credit Fund Transactions
class CreditFundTransactions(Base):
    __tablename__ = "credit_fund_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to credit_funds
    fund_id = Column(Integer, ForeignKey("credit_funds.fund_id"))
    transaction_date = Column(Date, nullable=False)  # Date of transaction
    transaction_type = Column(
        Enum("Buy", "Sell", name="transaction_type_enum"))
    # References the primary key of related asset (e.g., ISIN, ticker, property_id)
    asset_id = Column(String(255))
    amount = Column(DECIMAL(20, 2))  # Amount transacted
    price = Column(DECIMAL(20, 2))  # Transaction price

    # Relationships
    credit_fund = relationship("CreditFund")


# Table 6: Credit Fund Historical Data
class CreditFundHistoricalData(Base):
    __tablename__ = "credit_fund_historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to credit_funds
    fund_id = Column(Integer, ForeignKey("credit_funds.fund_id"))
    date = Column(Date, nullable=False)

    nav = Column(DECIMAL(20, 2))  # Net Asset Value
    total_assets = Column(DECIMAL(20, 2))  # Total assets under management
    expense_ratio = Column(DECIMAL(5, 2))
    yield_to_maturity = Column(DECIMAL(5, 2))
    average_duration = Column(DECIMAL(5, 2))
    return_percentage = Column(DECIMAL(5, 2))
    volatility = Column(DECIMAL(5, 2))
    sharpe_ratio = Column(DECIMAL(5, 2))

    # Relationships
    credit_fund = relationship("CreditFund")
