"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/ventureCapital/model.py
"""
from sqlalchemy import (
    Column, String, Integer, DECIMAL, Date, DateTime, ForeignKey, Enum, BigInteger, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enum for Investment Stages


class InvestmentStages:
    STAGES = [
        "Seed", "Pre-Series A", "Series A", "Series B", "Series C",
        "Growth", "Pre-IPO", "Other"
    ]

# Enum for Exit Types


class ExitTypes:
    EXITS = ["IPO", "Acquisition", "Buyback", "Liquidation", "Other"]

# Table 1: Venture Capital Firm Information


class VentureCapitalFirm(Base):
    __tablename__ = "vc_firms"

    firm_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    headquarters = Column(String(255))
    founded_year = Column(Integer)
    # Total capital under management
    total_funds_managed = Column(DECIMAL(20, 2))
    number_of_portfolio_companies = Column(Integer)

    # Relationships
    funds = relationship("Fund", back_populates="vc_firm",
                         cascade="all, delete-orphan")
    investments = relationship(
        "Investment", back_populates="vc_firm", cascade="all, delete-orphan"
    )


# Table 2: VC Funds Managed by Firms
class Fund(Base):
    __tablename__ = "vc_funds"

    fund_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    vc_firm_id = Column(Integer, ForeignKey(
        "vc_firms.firm_id"))  # Link to VC Firm
    fund_size = Column(DECIMAL(20, 2))  # Total fund size
    vintage_year = Column(Integer)  # Year the fund was launched
    # Sector focus (e.g., FinTech, Healthcare)
    focus_area = Column(String(255))
    current_status = Column(
        Enum("Active", "Closed", "Other", name="fund_status_enum"))

    # Relationships
    vc_firm = relationship("VentureCapitalFirm", back_populates="funds")
    investments = relationship(
        "Investment", back_populates="fund", cascade="all, delete-orphan")


# Table 3: Portfolio Companies
class PortfolioCompany(Base):
    __tablename__ = "portfolio_companies"

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    sector = Column(String(100))  # Industry or sector
    country = Column(String(50))  # Location
    year_founded = Column(Integer)
    stage = Column(Enum(*InvestmentStages.STAGES,
                   name="investment_stage_enum"))
    valuation = Column(DECIMAL(20, 2))  # Current valuation of the company
    status = Column(Enum("Active", "Exited", "Defunct",
                    name="company_status_enum"))

    # Relationships
    investments = relationship(
        "Investment", back_populates="portfolio_company", cascade="all, delete-orphan"
    )


# Table 4: Investments
class Investment(Base):
    __tablename__ = "investments"

    investment_id = Column(Integer, primary_key=True, autoincrement=True)
    vc_firm_id = Column(Integer, ForeignKey(
        "vc_firms.firm_id"))  # Link to VC Firm
    fund_id = Column(Integer, ForeignKey(
        "vc_funds.fund_id"))  # Link to VC Fund
    # Link to Portfolio Company
    company_id = Column(Integer, ForeignKey("portfolio_companies.company_id"))
    date = Column(Date, nullable=False)  # Date of the investment
    amount_invested = Column(DECIMAL(20, 2))  # Amount invested in the company
    equity_stake = Column(DECIMAL(10, 5))  # Ownership percentage acquired

    # Relationships
    vc_firm = relationship("VentureCapitalFirm", back_populates="investments")
    fund = relationship("Fund", back_populates="investments")
    portfolio_company = relationship(
        "PortfolioCompany", back_populates="investments")


# Table 5: Funding Rounds for Portfolio Companies
class FundingRound(Base):
    __tablename__ = "funding_rounds"

    round_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("portfolio_companies.company_id"))
    # Seed, Series A, etc.
    round_type = Column(
        Enum(*InvestmentStages.STAGES, name="funding_round_enum"))
    date = Column(Date, nullable=False)
    amount_raised = Column(DECIMAL(20, 2))  # Total amount raised in this round
    post_money_valuation = Column(DECIMAL(20, 2))  # Valuation after the round

    # Relationships
    portfolio_company = relationship(
        "PortfolioCompany", back_populates="funding_rounds")


# Table 6: Exits
class Exit(Base):
    __tablename__ = "exits"

    exit_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("portfolio_companies.company_id"))
    # IPO, Acquisition, etc.
    exit_type = Column(Enum(*ExitTypes.EXITS, name="exit_type_enum"))
    date = Column(Date, nullable=False)  # Date of the exit
    exit_valuation = Column(DECIMAL(20, 2))  # Valuation at the time of exit
    proceeds_to_firm = Column(DECIMAL(20, 2))  # Amount received by the VC firm

    # Relationships
    portfolio_company = relationship(
        "PortfolioCompany", back_populates="exits")


# Table 7: Metrics for Venture Capital Investments
class InvestmentMetrics(Base):
    __tablename__ = "investment_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("vc_funds.fund_id"))
    investment_id = Column(Integer, ForeignKey("investments.investment_id"))

    irr = Column(DECIMAL(5, 2))  # Internal Rate of Return
    tvpi = Column(DECIMAL(5, 2))  # Total Value to Paid-In
    dpi = Column(DECIMAL(5, 2))  # Distributions to Paid-In
    rvpi = Column(DECIMAL(5, 2))  # Residual Value to Paid-In

    # Relationships
    fund = relationship("Fund", back_populates="metrics")
    investment = relationship("Investment")


# Update Relationships for PortfolioCompany
PortfolioCompany.funding_rounds = relationship(
    "FundingRound", back_populates="portfolio_company", cascade="all, delete-orphan"
)
PortfolioCompany.exits = relationship(
    "Exit", back_populates="portfolio_company", cascade="all, delete-orphan"
)
