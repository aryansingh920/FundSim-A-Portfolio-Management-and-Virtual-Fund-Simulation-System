"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/loan/model.py
"""
from sqlalchemy import (
    Column, String, Integer, DECIMAL, DateTime, Date, ForeignKey, Text, Enum, Boolean
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Basic Loan Information


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(String(20), primary_key=True)  # Unique Loan Identifier
    loan_type = Column(Enum(
        "Personal", "Business", "Mortgage", "Auto", "Student", "Asset-Backed", "Other", name="loan_type_enum"
    ))  # Type of loan
    borrower_name = Column(String(255), nullable=False)  # Borrower's Name
    borrower_type = Column(Enum(
        "Individual", "Business", "Government", name="borrower_type_enum"
    ))  # Type of Borrower
    lender_name = Column(String(255))  # Lender's Name
    principal_amount = Column(DECIMAL(20, 2), nullable=False)  # Loan Amount
    # Annual Interest Rate (%)
    interest_rate = Column(DECIMAL(5, 2), nullable=False)
    repayment_frequency = Column(Enum(
        "Monthly", "Quarterly", "Annual", name="repayment_frequency_enum"
    ))  # Repayment Schedule
    start_date = Column(Date, nullable=False)  # Loan Start Date
    maturity_date = Column(Date, nullable=False)  # Loan Maturity Date
    loan_status = Column(Enum(
        "Active", "Closed", "Defaulted", "Restructured", name="loan_status_enum"
    ), default="Active")  # Loan Status
    currency = Column(String(3), ForeignKey(
        "currencies.iso_code"))  # Currency of Loan
    collateral_type = Column(Enum(
        "Real Estate", "Stock", "Bond", "Commodity", "Cash", "Other", name="collateral_type_enum"
    ), nullable=True)  # Type of Collateral
    collateral_value = Column(DECIMAL(20, 2))  # Collateral Value
    collateral_id = Column(String(20))  # ID of the collateral asset

    # Relationships
    repayment_schedule = relationship(
        "RepaymentSchedule", back_populates="loan", cascade="all, delete-orphan"
    )
    risk_metrics = relationship(
        "LoanRiskMetrics", back_populates="loan", cascade="all, delete-orphan"
    )
    historical_data = relationship(
        "LoanHistoricalData", back_populates="loan", cascade="all, delete-orphan"
    )

# Table 2: Repayment Schedule


class RepaymentSchedule(Base):
    __tablename__ = "repayment_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(20), ForeignKey(
        "loans.loan_id"))  # Foreign Key to loans
    due_date = Column(Date, nullable=False)  # Due Date for Payment
    amount_due = Column(DECIMAL(20, 2), nullable=False)  # Amount Due
    amount_paid = Column(DECIMAL(20, 2), default=0.00)  # Amount Paid
    payment_date = Column(Date)  # Actual Payment Date
    status = Column(Enum(
        "Due", "Paid", "Overdue", name="repayment_status_enum"
    ), default="Due")  # Status of the Repayment

    # Relationship
    loan = relationship("Loan", back_populates="repayment_schedule")

# Table 3: Loan Risk Metrics


class LoanRiskMetrics(Base):
    __tablename__ = "loan_risk_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(20), ForeignKey(
        "loans.loan_id"))  # Foreign Key to loans
    credit_score = Column(Integer)  # Borrower's Credit Score
    probability_of_default = Column(DECIMAL(5, 2))  # Likelihood of Default (%)
    # Expected Loss if Default Occurs (%)
    loss_given_default = Column(DECIMAL(5, 2))
    exposure_at_default = Column(DECIMAL(20, 2))  # Loan Amount at Risk
    interest_rate_spread = Column(DECIMAL(5, 2))  # Spread Over Benchmark Rate

    # Relationship
    loan = relationship("Loan", back_populates="risk_metrics")

# Table 4: Historical Data for Loans


class LoanHistoricalData(Base):
    __tablename__ = "loan_historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(20), ForeignKey(
        "loans.loan_id"))  # Foreign Key to loans
    date = Column(Date, nullable=False)  # Date of Record
    outstanding_balance = Column(DECIMAL(20, 2))  # Remaining Loan Balance
    amount_paid = Column(DECIMAL(20, 2))  # Amount Paid on this Date
    default_flag = Column(Boolean, default=False)  # Flag for Default

    # Relationship
    loan = relationship("Loan", back_populates="historical_data")

# Table 5: Collateral Information (Optional - Integration with Other Assets)


class Collateral(Base):
    __tablename__ = "collateral"

    # Unique Collateral Identifier
    collateral_id = Column(String(20), primary_key=True)
    loan_id = Column(String(20), ForeignKey("loans.loan_id"))  # Linked Loan
    collateral_type = Column(Enum(
        "Real Estate", "Stock", "Bond", "Commodity", "Cash", "Other", name="collateral_type_enum"
    ))  # Type of Collateral
    value = Column(DECIMAL(20, 2), nullable=False)  # Collateral Value
    linked_asset_id = Column(String(20))  # ID of Linked Asset (if applicable)
    description = Column(Text)  # Description of the Collateral

    # Relationship
    loan = relationship("Loan")
