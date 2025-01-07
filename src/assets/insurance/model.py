"""
Created on 07/01/2025

@author: Aryan

Filename: model.py

Relative Path: src/assets/insurance/model.py
"""
from sqlalchemy import (
    Column, String, Integer, DECIMAL, Date, DateTime, Enum, Text, ForeignKey, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enum for Insurance Types


class InsuranceType:
    CATEGORIES = ["Life", "Health", "Property",
                  "Vehicle", "Liability", "Travel", "Pet"]

# Table 1: Basic Insurance Policy Information


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    # Unique Policy Identifier
    policy_id = Column(String(20), primary_key=True)
    policy_name = Column(String(255), nullable=False)  # Policy Name/Title
    policy_type = Column(Enum(*InsuranceType.CATEGORIES,
                         name="policy_type_enum"))  # Policy Type
    issuer_id = Column(Integer, ForeignKey(
        "issuers.issuer_id"))  # Link to Issuer Table
    issue_date = Column(Date, nullable=False)  # Date of Policy Issuance
    expiration_date = Column(Date, nullable=False)  # Policy Expiration Date
    premium_amount = Column(DECIMAL(20, 2), nullable=False)  # Premium Amount
    coverage_amount = Column(DECIMAL(20, 2), nullable=False)  # Total Coverage
    deductible = Column(DECIMAL(20, 2), nullable=True)  # Deductible Amount
    currency = Column(String(10), nullable=False)  # Currency (e.g., USD, EUR)
    policy_status = Column(
        Enum("Active", "Expired", "Cancelled", "Pending", name="policy_status_enum"))

    # Relationships
    claims = relationship(
        "InsuranceClaim", back_populates="policy", cascade="all, delete-orphan"
    )
    risk_metrics = relationship(
        "InsuranceRiskMetrics", back_populates="policy", cascade="all, delete-orphan"
    )
    historical_data = relationship(
        "InsuranceHistoricalData", back_populates="policy", cascade="all, delete-orphan"
    )
    issuer = relationship("Issuer", back_populates="insurance_policies")


# Table 2: Claim Information
class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(20), ForeignKey("insurance_policies.policy_id"))
    claim_id = Column(String(20), nullable=False,
                      unique=True)  # Unique Claim Identifier
    claim_date = Column(Date, nullable=False)  # Date of Claim Filing
    claim_amount = Column(DECIMAL(20, 2), nullable=False)  # Claimed Amount
    # Amount Paid After Settlement
    settlement_amount = Column(DECIMAL(20, 2), nullable=True)
    claim_status = Column(
        Enum("Pending", "Approved", "Rejected", "Settled", name="claim_status_enum"))
    reason = Column(Text)  # Reason/Description of Claim
    claimant = Column(String(255), nullable=False)  # Name of the Claimant

    # Relationship
    policy = relationship("InsurancePolicy", back_populates="claims")


# Table 3: Risk Metrics
class InsuranceRiskMetrics(Base):
    __tablename__ = "insurance_risk_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(20), ForeignKey("insurance_policies.policy_id"))
    risk_score = Column(DECIMAL(5, 2))  # Risk Score (0 to 100 scale)
    probability_of_claim = Column(DECIMAL(5, 2))  # Probability of Claim (in %)
    # Total Claims Paid / Premiums Collected
    loss_ratio = Column(DECIMAL(5, 2))
    underwriting_profit_margin = Column(
        DECIMAL(5, 2))  # Underwriting Profit Margin %
    exposure_duration = Column(Integer)  # Exposure Duration in Days
    claim_frequency = Column(Integer)  # Number of Claims Per Year

    # Relationship
    policy = relationship("InsurancePolicy", back_populates="risk_metrics")


# Table 4: Historical Data
class InsuranceHistoricalData(Base):
    __tablename__ = "insurance_historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(20), ForeignKey("insurance_policies.policy_id"))
    date = Column(Date, nullable=False)

    premium_amount = Column(DECIMAL(20, 2))  # Premium Amount
    claims_paid = Column(DECIMAL(20, 2))  # Total Claims Paid on Date
    underwriting_profit = Column(DECIMAL(20, 2))  # Underwriting Profit on Date
    claim_frequency = Column(Integer)  # Claims Filed on Date
    risk_score = Column(DECIMAL(5, 2))  # Risk Score on Date

    # Relationship
    policy = relationship("InsurancePolicy", back_populates="historical_data")


# Table 5: Intraday Data (Optional)
class IntradayInsuranceData(Base):
    __tablename__ = "intraday_insurance_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(20), ForeignKey("insurance_policies.policy_id"))
    timestamp = Column(DateTime, nullable=False)  # Exact Time of the Record
    premium_amount = Column(DECIMAL(20, 2))  # Premium Amount at Timestamp
    risk_score = Column(DECIMAL(5, 2))  # Risk Score at Timestamp
    # Number of Claims in the Period
    claim_frequency = Column(Integer, nullable=False)

    # Relationship
    policy = relationship("InsurancePolicy")


# # Updating Issuer to Include Insurance Relationship
# Issuer.insurance_policies = relationship(
#     "InsurancePolicy", back_populates="issuer")
