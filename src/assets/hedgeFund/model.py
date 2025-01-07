"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/hedgeFund/model.py
"""

from sqlalchemy import (
    Column, String, Integer, DECIMAL, ForeignKey, Date, Text, Enum, DateTime, Boolean, Float
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Table 1: Hedge Fund Information


class HedgeFund(Base):
    __tablename__ = "hedge_funds"

    fund_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)  # Fund Name
    manager = Column(String(255), nullable=False)  # Fund Manager's Name
    inception_date = Column(Date, nullable=False)  # Date of Fund Creation
    fund_type = Column(Enum("Long/Short", "Market Neutral", "Event-Driven",
                            "Global Macro", "Quantitative", name="fund_type_enum"))
    # Total AUM (Assets Under Management)
    total_assets = Column(DECIMAL(20, 2), nullable=False)
    currency = Column(String(3), nullable=False,
                      default="USD")  # Fund Currency
    risk_tolerance = Column(
        Enum("High", "Medium", "Low", name="risk_tolerance_enum"))

    # Relationships
    allocations = relationship(
        "HedgeFundAllocation", back_populates="hedge_fund", cascade="all, delete-orphan"
    )
    performance_metrics = relationship(
        "HedgeFundPerformance", back_populates="hedge_fund", cascade="all, delete-orphan"
    )


# Table 2: Hedge Fund Allocations
class HedgeFundAllocation(Base):
    __tablename__ = "hedge_fund_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("hedge_funds.fund_id"))
    asset_type = Column(Enum("Stock", "Commodity", "Bond",
                        "RealEstate", "Currency", name="asset_type_enum"))
    # Generic Asset Identifier (e.g., Ticker, ISIN)
    asset_id = Column(String(255), nullable=False)
    allocation_percentage = Column(DECIMAL(5, 2))  # % of total portfolio
    acquisition_date = Column(Date, nullable=False)  # Date of Acquisition
    exit_date = Column(Date)  # Date of Exit (if applicable)
    current_value = Column(DECIMAL(20, 2))  # Current Value of the Asset
    strategy = Column(Text)  # Investment Strategy for this asset
    # JSON/Text representation of specific risk metrics
    risk_metrics = Column(Text)

    # Relationships
    hedge_fund = relationship("HedgeFund", back_populates="allocations")


# Table 3: Hedge Fund Performance Metrics
class HedgeFundPerformance(Base):
    __tablename__ = "hedge_fund_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("hedge_funds.fund_id"))
    date = Column(Date, nullable=False)  # Reporting Date
    net_asset_value = Column(DECIMAL(20, 2))  # NAV per share
    return_percentage = Column(DECIMAL(5, 2))  # Monthly/Quarterly Return (%)
    sharpe_ratio = Column(DECIMAL(5, 2))  # Risk-adjusted return metric
    sortino_ratio = Column(DECIMAL(5, 2))  # Downside risk-adjusted return
    alpha = Column(DECIMAL(5, 2))  # Excess return compared to benchmark
    beta = Column(DECIMAL(5, 2))  # Sensitivity to market movements
    volatility = Column(DECIMAL(5, 2))  # Standard deviation of returns

    # Relationships
    hedge_fund = relationship(
        "HedgeFund", back_populates="performance_metrics")


# Table 4: Hedge Fund Risk Exposure
class HedgeFundRiskExposure(Base):
    __tablename__ = "hedge_fund_risk_exposure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("hedge_funds.fund_id"))
    date = Column(Date, nullable=False)  # Reporting Date
    # % of exposure to the overall market
    market_exposure = Column(DECIMAL(5, 2))
    # JSON/Text representation of sector-wise allocation
    sector_exposure = Column(Text)
    # JSON/Text representation of geographic allocation
    geographic_exposure = Column(Text)
    # JSON/Text representation of currency allocation
    currency_exposure = Column(Text)
    leverage_ratio = Column(DECIMAL(5, 2))  # Leverage used in the fund

    # Relationships
    hedge_fund = relationship("HedgeFund")


# Table 5: Hedge Fund Transactions
class HedgeFundTransaction(Base):
    __tablename__ = "hedge_fund_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("hedge_funds.fund_id"))
    asset_type = Column(Enum("Stock", "Commodity", "Bond",
                        "RealEstate", "Currency", name="asset_type_enum"))
    asset_id = Column(String(255), nullable=False)  # Identifier of the asset
    transaction_type = Column(
        Enum("Buy", "Sell", "Short", "Cover", name="transaction_type_enum"))
    transaction_date = Column(DateTime, nullable=False)
    transaction_price = Column(DECIMAL(20, 2))  # Price of the transaction
    transaction_volume = Column(DECIMAL(20, 2))  # Volume/Units traded
    # Cost of transaction (fees, commissions)
    transaction_cost = Column(DECIMAL(10, 2))

    # Relationships
    hedge_fund = relationship("HedgeFund")


# Table 6: Hedge Fund Strategy Breakdown
class HedgeFundStrategy(Base):
    __tablename__ = "hedge_fund_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("hedge_funds.fund_id"))
    strategy_name = Column(String(255), nullable=False)  # Name of the strategy
    description = Column(Text)  # Description of the strategy
    # % of total fund allocated to this strategy
    allocation_percentage = Column(DECIMAL(5, 2))

    # Relationships
    hedge_fund = relationship("HedgeFund")
