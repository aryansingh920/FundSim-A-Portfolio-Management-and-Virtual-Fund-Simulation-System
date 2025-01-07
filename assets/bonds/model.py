from sqlalchemy import (
    Column, DateTime, String, Integer, DECIMAL, ForeignKey, BigInteger, Date, Enum, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Basic Bond Information


class Bond(Base):
    __tablename__ = "bonds"

    # International Securities Identification Number
    isin = Column(String(12), primary_key=True)
    cusip = Column(String(9), unique=True, nullable=True)  # US bond identifier
    bond_name = Column(String(255), nullable=False)
    # Name of the bond issuer (e.g., company, government)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(Date, nullable=False)  # Bond issuance date
    maturity_date = Column(Date, nullable=False)  # Bond maturity date
    coupon_rate = Column(DECIMAL(5, 2))  # Fixed coupon rate in percentage
    coupon_frequency = Column(Enum(
        "Annual", "Semi-Annual", "Quarterly", "Monthly", name="coupon_frequency_enum"))
    # Par value of the bond
    face_value = Column(DECIMAL(20, 2), nullable=False)
    bond_type = Column(Enum("Corporate", "Government", "Municipal",
                       "Treasury", "Agency", name="bond_type_enum"))
    # Currency of the bond (e.g., USD, EUR)
    currency = Column(String(10), nullable=False)
    # Whether the bond is callable (1 for True, 0 for False)
    callable = Column(Integer, default=0)
    # Whether the bond is puttable (1 for True, 0 for False)
    puttable = Column(Integer, default=0)
    # Whether the bond is convertible into equity (1 for True, 0 for False)
    convertible = Column(Integer, default=0)
    market = Column(String(50))  # Market or exchange where the bond is traded
    # Sector classification of the bond (e.g., Technology, Government)
    sector = Column(String(100))

    # Historical data tracking
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationships
    coupons = relationship(
        "CouponPayment", back_populates="bond", cascade="all, delete-orphan")
    risk_metrics = relationship(
        "BondRiskMetrics", back_populates="bond", cascade="all, delete-orphan")
    ratings = relationship(
        "BondRating", back_populates="bond", cascade="all, delete-orphan")
    historical_data = relationship(
        "BondHistoricalData", back_populates="bond", cascade="all, delete-orphan")
    intraday_data = relationship(
        "BondIntradayData", back_populates="bond", cascade="all, delete-orphan")


# Table 2: Coupon Payments
class CouponPayment(Base):
    __tablename__ = "coupon_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String(12), ForeignKey("bonds.isin"))  # Foreign Key to bonds
    payment_date = Column(Date, nullable=False)  # Date of coupon payment
    # Amount paid as a coupon
    payment_amount = Column(DECIMAL(20, 2), nullable=False)

    # Relationship
    bond = relationship("Bond", back_populates="coupons")


# Table 3: Bond Ratings
class BondRating(Base):
    __tablename__ = "bond_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String(12), ForeignKey("bonds.isin"))  # Foreign Key to bonds
    # Name of the rating agency (e.g., S&P, Moody's)
    rating_agency = Column(String(100), nullable=False)
    # Credit rating (e.g., AAA, BBB)
    credit_rating = Column(String(10), nullable=False)
    outlook = Column(Enum("Stable", "Positive", "Negative",
                     "Developing", name="outlook_enum"))
    rating_date = Column(Date, nullable=False)  # Date of rating

    # Relationship
    bond = relationship("Bond", back_populates="ratings")


# Table 4: Bond Risk Metrics
class BondRiskMetrics(Base):
    __tablename__ = "bond_risk_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String(12), ForeignKey("bonds.isin"))  # Foreign Key to bonds
    duration = Column(DECIMAL(10, 2))  # Macaulay Duration
    modified_duration = Column(DECIMAL(10, 2))  # Modified Duration
    convexity = Column(DECIMAL(10, 2))  # Convexity of the bond
    yield_to_maturity = Column(DECIMAL(10, 2))  # Yield to maturity
    current_yield = Column(DECIMAL(10, 2))  # Current yield
    # Spread to benchmark Treasury bond
    spread_to_treasury = Column(DECIMAL(10, 2))

    # Relationship
    bond = relationship("Bond", back_populates="risk_metrics")


# Table 5: Historical Data
class BondHistoricalData(Base):
    __tablename__ = "bond_historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String(12), ForeignKey("bonds.isin"))
    date = Column(Date, nullable=False)

    open_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))
    day_high = Column(DECIMAL(10, 2))
    day_low = Column(DECIMAL(10, 2))
    trading_volume = Column(BigInteger)

    # Relationship back to Bond
    bond = relationship("Bond", back_populates="historical_data")


# Table 6: Intraday Data
class BondIntradayData(Base):
    __tablename__ = "bond_intraday_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String(12), ForeignKey("bonds.isin"))
    timestamp = Column(DateTime, nullable=False)  # Exact time for the record
    # Bond price at the timestamp
    price = Column(DECIMAL(10, 2), nullable=False)
    volume = Column(BigInteger, default=0)  # Trading volume at the timestamp

    # Relationship back to Bond
    bond = relationship("Bond", back_populates="intraday_data")


# Table 7: Issuer Information
class Issuer(Base):
    __tablename__ = "issuers"

    issuer_id = Column(Integer, primary_key=True, autoincrement=True)
    # Issuer name (e.g., Government of USA, Apple Inc.)
    name = Column(String(255), nullable=False, unique=True)
    sector = Column(String(100))  # Sector of the issuer
    country = Column(String(50))  # Country of the issuer

    # Relationships
    bonds = relationship("Bond", back_populates="issuer")


# Updating Bond to include Issuer Relationship
Bond.issuer_id = Column(Integer, ForeignKey("issuers.issuer_id"))
Bond.issuer = relationship("Issuer", back_populates="bonds")
