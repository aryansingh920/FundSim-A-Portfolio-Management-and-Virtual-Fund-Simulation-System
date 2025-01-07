from sqlalchemy import (
    Column, String, Integer, DECIMAL, ForeignKey, Date, DateTime, Text, Boolean, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Table 1: Basic Property Information


class Property(Base):
    __tablename__ = "properties"

    property_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Property Name
    property_type = Column(String(50))  # Residential, Commercial, Industrial
    address = Column(Text, nullable=False)  # Full Address
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(10), nullable=False)
    country = Column(String(100), nullable=False)
    size_in_sqft = Column(DECIMAL(10, 2))  # Size in square feet
    year_built = Column(Integer)  # Year the property was constructed
    num_units = Column(Integer, default=1)  # Number of rental/sale units
    occupancy_rate = Column(DECIMAL(5, 2), default=0.0)  # Occupied/Total Units

    # New Columns for Tracking Historical Data
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationships
    financial_metrics = relationship(
        "FinancialMetrics", back_populates="property", cascade="all, delete-orphan"
    )
    market_indicators = relationship(
        "MarketIndicators", back_populates="property", cascade="all, delete-orphan"
    )
    transaction_history = relationship(
        "TransactionHistory", back_populates="property", cascade="all, delete-orphan"
    )
    tenant_info = relationship(
        "TenantInfo", back_populates="property", cascade="all, delete-orphan"
    )
    historical_data = relationship(
        "HistoricalData", back_populates="property", cascade="all, delete-orphan"
    )


# Table 2: Financial Metrics
class FinancialMetrics(Base):
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    rental_income = Column(DECIMAL(20, 2))  # Monthly or Annual Rental Income
    # Maintenance, Taxes, Insurance
    operating_expenses = Column(DECIMAL(20, 2))
    net_operating_income = Column(DECIMAL(20, 2))  # Income after expenses
    cap_rate = Column(DECIMAL(5, 2))  # NOI / Property Value
    cash_flow = Column(DECIMAL(20, 2))  # After debt service
    mortgage_balance = Column(DECIMAL(20, 2))  # Outstanding mortgage
    loan_to_value_ratio = Column(DECIMAL(5, 2))  # Loan/Property Value

    # New Columns for Tracking Historical Data
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship
    property = relationship("Property", back_populates="financial_metrics")


# Table 3: Market Indicators
class MarketIndicators(Base):
    __tablename__ = "market_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    avg_price_per_sqft = Column(DECIMAL(10, 2))  # Local Market Average
    market_rent_per_sqft = Column(DECIMAL(10, 2))  # Local Market Average Rent
    # Market Trend Analysis (e.g., Increasing/Decreasing)
    occupancy_trend = Column(Text)
    market_value = Column(DECIMAL(20, 2))  # Estimated Market Value
    # % increase in property value over time
    appreciation_rate = Column(DECIMAL(5, 2))

    # New Columns for Tracking Historical Data
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship
    property = relationship("Property", back_populates="market_indicators")


# Table 4: Transaction History
class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(50))  # Purchase, Sale, Lease
    transaction_price = Column(DECIMAL(20, 2))  # Price at transaction
    buyer = Column(String(255))  # Buyer Information
    seller = Column(String(255))  # Seller Information

    # Relationship
    property = relationship("Property", back_populates="transaction_history")


# Table 5: Tenant Information
class TenantInfo(Base):
    __tablename__ = "tenant_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    unit_number = Column(String(10))  # Unit Identifier
    tenant_name = Column(String(255), nullable=False)
    lease_start_date = Column(Date, nullable=False)
    lease_end_date = Column(Date)
    monthly_rent = Column(DECIMAL(10, 2))
    security_deposit = Column(DECIMAL(10, 2))

    # Relationship
    property = relationship("Property", back_populates="tenant_info")


# Table 6: Historical Data
class HistoricalData(Base):
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    date = Column(Date, nullable=False)

    market_value = Column(DECIMAL(20, 2))
    rental_income = Column(DECIMAL(20, 2))
    operating_expenses = Column(DECIMAL(20, 2))
    net_operating_income = Column(DECIMAL(20, 2))
    cap_rate = Column(DECIMAL(5, 2))
    cash_flow = Column(DECIMAL(20, 2))

    avg_price_per_sqft = Column(DECIMAL(10, 2))
    market_rent_per_sqft = Column(DECIMAL(10, 2))
    occupancy_rate = Column(DECIMAL(5, 2))

    # Relationship
    property = relationship("Property", back_populates="historical_data")


# Table 7: Intraday Data (Optional for Real-Time Analytics)
class IntradayData(Base):
    __tablename__ = "intraday_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    timestamp = Column(DateTime, nullable=False)  # Exact time for the record
    market_value = Column(DECIMAL(20, 2))  # Real-time property valuation
    occupancy_rate = Column(DECIMAL(5, 2))  # Real-time occupancy

    # Relationship
    property = relationship("Property")
