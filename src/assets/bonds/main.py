"""
Created on 07/01/2025

@author: Aryan

Filename: main.py

Relative Path: src/assets/bonds/main.py
"""

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from assets.bonds.model import Base, BondHistoricalData, BondRating, BondRiskMetrics, CouponPayment
from assets.bonds.create_historical_data import create_and_insert_historical_bond_data


def main(number_of_bonds: int = 1, days: int = 365):
    """
    Main function to generate bond data, including historical data, coupon payments, risk metrics, and ratings.

    Args:
        number_of_bonds (int): Number of bonds to generate.
        days (int): Number of days for historical data generation.

    Returns:
        dict: A dictionary containing all generated bond data.
    """
    # Dictionary to store all generated bond data
    all_bond_data = {}

    # Setup the database connection
    engine = create_engine('sqlite:///data/bonds.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for _ in range(number_of_bonds):
        # Generate random bond details
        isin = f"US{random.randint(100000000, 999999999)}"
        face_value = random.uniform(500, 10000)
        coupon_rate = random.uniform(1.0, 10.0)
        maturity_date = datetime.now() + timedelta(days=random.randint(365, 365 * 30))
        issue_date = datetime.now() - timedelta(days=random.randint(0, 365 * 5))

        # Create and insert bond data into the database
        create_and_insert_historical_bond_data(
            session=session,
            isin=isin,
            face_value=face_value,
            coupon_rate=coupon_rate,
            maturity_date=maturity_date,
            issue_date=issue_date,
            days=days
        )

        # Fetch the generated historical data for the bond
        historical_records = (
            session.query(BondHistoricalData)
            .filter_by(isin=isin)
            .order_by(BondHistoricalData.date.asc())
            .all()
        )

        # Fetch the generated coupon payments for the bond
        coupon_records = (
            session.query(CouponPayment)
            .filter_by(isin=isin)
            .order_by(CouponPayment.payment_date.asc())
            .all()
        )

        # Fetch the generated risk metrics for the bond
        risk_metrics = (
            session.query(BondRiskMetrics)
            .filter_by(isin=isin)
            .first()
        )

        # Fetch the generated bond rating for the bond
        bond_rating = (
            session.query(BondRating)
            .filter_by(isin=isin)
            .first()
        )

        # Collect all data for the current bond
        bond_data = {
            "bond_info": {
                "isin": isin,
                "face_value": face_value,
                "coupon_rate": coupon_rate,
                "maturity_date": maturity_date.strftime("%Y-%m-%d"),
                "issue_date": issue_date.strftime("%Y-%m-%d"),
            },
            "historical_data": [
                {
                    "date": record.date,
                    "open_price": record.open_price,
                    "close_price": record.close_price,
                    "day_high": record.day_high,
                    "day_low": record.day_low,
                    "trading_volume": record.trading_volume
                }
                for record in historical_records
            ],
            "coupon_payments": [
                {
                    "payment_date": payment.payment_date,
                    "payment_amount": payment.payment_amount
                }
                for payment in coupon_records
            ],
            "risk_metrics": {
                "duration": risk_metrics.duration,
                "modified_duration": risk_metrics.modified_duration,
                "convexity": risk_metrics.convexity,
                "yield_to_maturity": risk_metrics.yield_to_maturity,
                "current_yield": risk_metrics.current_yield,
                "spread_to_treasury": risk_metrics.spread_to_treasury
            },
            "bond_rating": {
                "rating_agency": bond_rating.rating_agency,
                "credit_rating": bond_rating.credit_rating,
                "outlook": bond_rating.outlook,
                "rating_date": bond_rating.rating_date.strftime("%Y-%m-%d")
            }
        }

        # Add to the comprehensive dictionary
        all_bond_data[isin] = bond_data

    print(f"Total bonds generated: {len(all_bond_data)}")
    session.close()
    return all_bond_data


if __name__ == "__main__":
    # Generate data for 3 bonds
    main(number_of_bonds=3)
