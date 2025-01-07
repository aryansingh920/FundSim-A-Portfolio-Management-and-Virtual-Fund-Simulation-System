"""
Created on 07/01/2025

@author: Aryan

Filename: create_historical_data.py

Relative Path: src/assets/bonds/create_historical_data.py
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from assets.bonds.model import (
    Bond, BondHistoricalData, BondRiskMetrics, BondRating, CouponPayment
)
from assets.bonds.historical_data import BondDataGenerator


def create_and_insert_historical_bond_data(
    session: Session,
    isin: str,
    face_value: float,
    coupon_rate: float,
    maturity_date: datetime,
    issue_date: datetime,
    days: int,
    annual_yield: float = 5.0,
    base_volume: int = 100_000
):
    """
    Generate and insert historical data, coupon payments, risk metrics, and ratings for a bond.

    Args:
        session (Session): SQLAlchemy session for database operations.
        isin (str): ISIN identifier for the bond.
        face_value (float): The par value of the bond.
        coupon_rate (float): Annual coupon rate in percentage.
        maturity_date (datetime): Maturity date of the bond.
        issue_date (datetime): Issue date of the bond.
        days (int): Number of days to generate historical data for.
        annual_yield (float, optional): Estimated annual yield for the bond. Defaults to 5.0.
        base_volume (int, optional): Base trading volume for the bond. Defaults to 100,000.

    Returns:
        None
    """
    # Initialize the data generator
    generator = BondDataGenerator(
        isin=isin,
        face_value=face_value,
        coupon_rate=coupon_rate,
        maturity_date=maturity_date,
        issue_date=issue_date,
        annual_yield=annual_yield,
        base_volume=base_volume
    )

    # Generate historical data
    print(f"Generating historical data for bond {isin}...")
    historical_data = generator.generate_historical_data(days)
    generator.store_historical_data(session, historical_data)

    # Generate coupon payments
    print(f"Generating coupon payments for bond {isin}...")
    coupon_payments = generator.generate_coupon_payments()
    generator.store_coupon_payments(session, coupon_payments)

    # Generate risk metrics
    print(f"Generating risk metrics for bond {isin}...")
    risk_metrics = generator.generate_risk_metrics()
    generator.store_risk_metrics(session, risk_metrics)

    # Generate bond rating
    print(f"Generating bond rating for bond {isin}...")
    bond_rating = generator.generate_bond_rating()
    generator.store_bond_rating(session, bond_rating)

    print(f"All data for bond {isin} successfully created and stored.")


def create_historical_data_for_bonds(
    session: Session,
    bonds_info: list
):
    """
    Create and insert historical data for multiple bonds.

    Args:
        session (Session): SQLAlchemy session for database operations.
        bonds_info (list): List of bond details. Each item is a dictionary with keys:
            - isin
            - face_value
            - coupon_rate
            - maturity_date
            - issue_date
            - days
            - annual_yield (optional)
            - base_volume (optional)

    Returns:
        None
    """
    for bond in bonds_info:
        try:
            create_and_insert_historical_bond_data(
                session=session,
                isin=bond["isin"],
                face_value=bond["face_value"],
                coupon_rate=bond["coupon_rate"],
                maturity_date=bond["maturity_date"],
                issue_date=bond["issue_date"],
                days=bond["days"],
                annual_yield=bond.get("annual_yield", 5.0),
                base_volume=bond.get("base_volume", 100_000)
            )
        except Exception as e:
            print(f"Error while processing bond {bond['isin']}: {e}")


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Example database URL; replace with your actual database connection string
    DATABASE_URL = "sqlite:///bonds.db"

    # Initialize the database session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # Example bond data
    bonds_info = [
        {
            "isin": "US1234567890",
            "face_value": 1000,
            "coupon_rate": 5.0,
            "maturity_date": datetime(2035, 12, 31),
            "issue_date": datetime(2025, 1, 1),
            "days": 365 * 10
        },
        {
            "isin": "US9876543210",
            "face_value": 500,
            "coupon_rate": 3.0,
            "maturity_date": datetime(2030, 12, 31),
            "issue_date": datetime(2020, 1, 1),
            "days": 365 * 5
        }
    ]

    # Create historical data for bonds
    create_historical_data_for_bonds(session, bonds_info)

    # Close the session
    session.close()
