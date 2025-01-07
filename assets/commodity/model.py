"""
Created on 07/01/2025

@author: Aryan

Filename: commodity_model.py

Relative Path: src/assets/commodities/commodity_model.py
"""

from sqlalchemy import (
    Column, DateTime, String, Integer, DECIMAL, ForeignKey, BigInteger, Date, Float, Enum, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enum for units of measurement


class MeasurementUnits:
    WEIGHT = ["kg", "ton", "lb"]
    VOLUME = ["litre", "barrel", "gallon"]
    LENGTH = ["meter", "feet"]
    ENERGY = ["MMBtu", "kWh"]
    OTHER = ["unit", "oz", "gram"]

# Table 1: Basic Commodity Information


class Commodity(Base):
    __tablename__ = "commodities"

    # Unique identifier for the commodity
    commodity_id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)  # Commodity name
    category = Column(String(100))  # E.g., Metal, Energy, Agricultural
    # Unit of measurement (e.g., kg, barrel)
    unit_of_measurement = Column(String(20))
    # JSON/Text representation of physical properties (density, state, etc.)
    physical_properties = Column(Text)
    # Primary origin of the commodity
    geographical_origin = Column(String(255))
    # JSON/Text representation of exchanges where traded
    traded_exchanges = Column(Text)
    # JSON/Text for capturing seasonal patterns (e.g., harvest periods)
    seasonality = Column(Text)

    # Relationships
    price_trading_info = relationship(
        "CommodityPriceTradingInfo", back_populates="commodity")
    fundamental_metrics = relationship(
        "CommodityFundamentalMetrics", back_populates="commodity")
    historical_data = relationship(
        "CommodityHistoricalData", back_populates="commodity", cascade="all, delete-orphan")
    volatility_risk = relationship(
        "CommodityVolatilityRisk", back_populates="commodity")

# Table 2: Price and Trading Information


class CommodityPriceTradingInfo(Base):
    __tablename__ = "commodity_price_trading_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity_id = Column(String(20), ForeignKey(
        "commodities.commodity_id"))  # Foreign Key to commodities
    current_price = Column(DECIMAL(10, 2))  # Current trading price per unit
    open_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))
    day_high = Column(DECIMAL(10, 2))
    day_low = Column(DECIMAL(10, 2))
    week_52_high = Column(DECIMAL(10, 2))
    week_52_low = Column(DECIMAL(10, 2))
    trading_volume = Column(BigInteger)
    average_volume = Column(BigInteger)
    # Cost of storing the commodity per unit
    storage_cost = Column(DECIMAL(10, 2))
    # Cost of transportation per unit
    transportation_cost = Column(DECIMAL(10, 2))

    # New columns to track historical data range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship
    commodity = relationship("Commodity", back_populates="price_trading_info")

# Table 3: Fundamental Metrics


class CommodityFundamentalMetrics(Base):
    __tablename__ = "commodity_fundamental_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity_id = Column(String(20), ForeignKey(
        "commodities.commodity_id"))  # Foreign Key to commodities
    global_supply = Column(BigInteger)  # Global supply in the chosen unit
    global_demand = Column(BigInteger)  # Global demand in the chosen unit
    production_cost = Column(DECIMAL(10, 2))  # Cost to produce per unit
    # Percentage of storage availability
    storage_availability = Column(DECIMAL(10, 2))
    seasonal_demand_variation = Column(
        DECIMAL(5, 2))  # Seasonal variation in demand
    inflation_impact = Column(DECIMAL(5, 2))  # Impact of inflation on price
    # Scale from 0-10 for risk due to geopolitical factors
    geopolitical_risk = Column(DECIMAL(5, 2))

    # New columns to track historical data range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship
    commodity = relationship("Commodity", back_populates="fundamental_metrics")

# Table 4: Volatility and Risk Metrics


class CommodityVolatilityRisk(Base):
    __tablename__ = "commodity_volatility_risk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity_id = Column(String(20), ForeignKey(
        "commodities.commodity_id"))  # Foreign Key to commodities
    beta = Column(DECIMAL(5, 2))  # Volatility in comparison to a benchmark
    standard_deviation = Column(DECIMAL(5, 2))  # Price variation
    sharpe_ratio = Column(DECIMAL(5, 2))  # Risk-adjusted return
    hedging_cost = Column(DECIMAL(10, 2))  # Cost of hedging risk per unit
    # Correlation coefficient with equity markets
    correlation_with_equities = Column(DECIMAL(5, 2))

    # New columns to track historical data range
    historical_data_start_date = Column(Date)
    historical_data_end_date = Column(Date)

    # Relationship
    commodity = relationship("Commodity", back_populates="volatility_risk")

# Table 5: Historical Data


class CommodityHistoricalData(Base):
    __tablename__ = "commodity_historical_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity_id = Column(String(20), ForeignKey("commodities.commodity_id"))
    date = Column(Date, nullable=False)

    open_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))
    day_high = Column(DECIMAL(10, 2))
    day_low = Column(DECIMAL(10, 2))

    week_52_high = Column(DECIMAL(10, 2))
    week_52_low = Column(DECIMAL(10, 2))

    trading_volume = Column(BigInteger)
    average_volume = Column(BigInteger)

    global_supply = Column(BigInteger)
    global_demand = Column(BigInteger)
    production_cost = Column(DECIMAL(10, 2))
    storage_cost = Column(DECIMAL(10, 2))
    transportation_cost = Column(DECIMAL(10, 2))

    beta = Column(DECIMAL(5, 2))
    standard_deviation = Column(DECIMAL(5, 2))
    sharpe_ratio = Column(DECIMAL(5, 2))

    # Relationship back to Commodity
    commodity = relationship("Commodity", back_populates="historical_data")
