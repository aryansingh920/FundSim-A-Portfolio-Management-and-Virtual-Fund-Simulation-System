"""
Created on 07/01/2025

@author: Aryan

Filename: historical_data.py

Relative Path: src/assets/bonds/historical_data.py
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import math
import statistics
from assets.bonds.model import BondHistoricalData, CouponPayment, BondRiskMetrics, BondRating

from sqlalchemy.orm import Session
from assets.bonds.model import (
    Bond, BondHistoricalData, BondRiskMetrics, BondRating, CouponPayment
)


class BondDataGenerator:
    def __init__(
        self,
        isin: str,
        face_value: float,
        coupon_rate: float,
        maturity_date: datetime,
        issue_date: datetime,
        annual_yield: float = 5.0,
        base_volume: int = 100_000,
    ):
        """
        Initialize parameters for bond data generation.
        """
        self.isin = isin
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.maturity_date = maturity_date
        self.issue_date = issue_date
        self.annual_yield = annual_yield
        self.base_volume = base_volume

        # Calculate the annual drift and volatility for bond prices
        self.annual_drift = self._calculate_annual_drift()
        self.annual_volatility = self._calculate_annual_volatility()

        # Convert annual parameters to daily
        self.daily_mu = self.annual_drift / 252
        self.daily_sigma = self.annual_volatility / (252 ** 0.5)

    def _calculate_annual_drift(self) -> float:
        """
        Calculate annual drift (mu) based on coupon rate and annual yield.
        """
        return self.coupon_rate / 100.0 + (self.annual_yield / 100.0)

    def _calculate_annual_volatility(self) -> float:
        """
        Estimate annual volatility based on bond type and market conditions.
        Typically lower for bonds than stocks.
        """
        return random.uniform(0.05, 0.15)

    def _simulate_price(self, prev_price: float) -> float:
        """
        Simulate next day's price using Geometric Brownian Motion.
        S_{t+1} = S_t * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        """
        dt = 1 / 252
        z = random.gauss(0, 1)
        drift_term = (self.daily_mu - 0.5 * self.daily_sigma**2) * dt
        diffusion_term = self.daily_sigma * math.sqrt(dt) * z
        return prev_price * math.exp(drift_term + diffusion_term)

    def generate_historical_data(self, days: int) -> List[Dict[str, Any]]:
        """
        Generate daily historical bond data for the given number of days.
        """
        data = []
        current_date = self.issue_date
        prev_price = self.face_value  # Start with face value

        for _ in range(days):
            if current_date >= self.maturity_date:
                break

            close_price = self._simulate_price(prev_price)
            day_high = close_price * random.uniform(1.001, 1.01)
            day_low = close_price * random.uniform(0.99, 0.999)

            volume = random.randint(
                int(self.base_volume * 0.8), int(self.base_volume * 1.2))

            data.append({
                "isin": self.isin,
                "date": current_date,
                "open_price": round(prev_price, 2),
                "close_price": round(close_price, 2),
                "day_high": round(day_high, 2),
                "day_low": round(day_low, 2),
                "trading_volume": volume
            })

            prev_price = close_price
            current_date += timedelta(days=1)

        return data

    def generate_coupon_payments(self) -> List[Dict[str, Any]]:
        """
        Generate a list of coupon payments for the bond's lifetime.
        """
        frequency = 12 / self.coupon_rate if self.coupon_rate > 0 else 1
        payment_dates = []
        current_date = self.issue_date

        while current_date < self.maturity_date:
            current_date += timedelta(days=int(365 / frequency))
            if current_date > self.maturity_date:
                break
            payment_dates.append(current_date)

        return [{
            "isin": self.isin,
            "payment_date": payment_date,
            "payment_amount": round(self.face_value * (self.coupon_rate / 100) / frequency, 2)
        } for payment_date in payment_dates]

    def generate_risk_metrics(self) -> Dict[str, Any]:
        """
        Generate bond risk metrics.
        """
        duration = random.uniform(1, 15)
        modified_duration = duration * random.uniform(0.8, 1.2)
        convexity = random.uniform(0.1, 5)
        yield_to_maturity = self.annual_yield
        current_yield = self.coupon_rate

        return {
            "isin": self.isin,
            "duration": round(duration, 2),
            "modified_duration": round(modified_duration, 2),
            "convexity": round(convexity, 2),
            "yield_to_maturity": round(yield_to_maturity, 2),
            "current_yield": round(current_yield, 2),
            "spread_to_treasury": round(random.uniform(0, 5), 2)
        }

    def generate_bond_rating(self) -> Dict[str, Any]:
        """
        Generate a bond rating record.
        """
        return {
            "isin": self.isin,
            "rating_agency": random.choice(["S&P", "Moody's", "Fitch"]),
            "credit_rating": random.choice(["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"]),
            "outlook": random.choice(["Stable", "Positive", "Negative", "Developing"]),
            "rating_date": self.issue_date + timedelta(days=random.randint(0, 365))
        }

    def store_historical_data(self, session: Session, historical_data: List[Dict[str, Any]]):
        """
        Insert generated historical data into the database.
        """
        records = [
            BondHistoricalData(
                isin=entry["isin"],
                date=entry["date"],
                open_price=entry["open_price"],
                close_price=entry["close_price"],
                day_high=entry["day_high"],
                day_low=entry["day_low"],
                trading_volume=entry["trading_volume"]
            ) for entry in historical_data
        ]
        session.bulk_save_objects(records)
        session.commit()

    def store_coupon_payments(self, session: Session, coupon_payments: List[Dict[str, Any]]):
        """
        Insert generated coupon payments into the database.
        """
        records = [
            CouponPayment(
                isin=entry["isin"],
                payment_date=entry["payment_date"],
                payment_amount=entry["payment_amount"]
            ) for entry in coupon_payments
        ]
        session.bulk_save_objects(records)
        session.commit()

    def store_risk_metrics(self, session: Session, risk_metrics: Dict[str, Any]):
        """
        Insert generated risk metrics into the database.
        """
        record = BondRiskMetrics(
            isin=risk_metrics["isin"],
            duration=risk_metrics["duration"],
            modified_duration=risk_metrics["modified_duration"],
            convexity=risk_metrics["convexity"],
            yield_to_maturity=risk_metrics["yield_to_maturity"],
            current_yield=risk_metrics["current_yield"],
            spread_to_treasury=risk_metrics["spread_to_treasury"]
        )
        session.add(record)
        session.commit()

    def store_bond_rating(self, session: Session, bond_rating: Dict[str, Any]):
        """
        Insert generated bond rating into the database.
        """
        record = BondRating(
            isin=bond_rating["isin"],
            rating_agency=bond_rating["rating_agency"],
            credit_rating=bond_rating["credit_rating"],
            outlook=bond_rating["outlook"],
            rating_date=bond_rating["rating_date"]
        )
        session.add(record)
        session.commit()


def create_and_insert_bond_data(
    session: Session,
    isin: str,
    face_value: float,
    coupon_rate: float,
    maturity_date: datetime,
    issue_date: datetime,
    days: int
):
    """
    Wrapper function to create and insert all bond-related data.
    """
    generator = BondDataGenerator(
        isin=isin,
        face_value=face_value,
        coupon_rate=coupon_rate,
        maturity_date=maturity_date,
        issue_date=issue_date
    )

    # Generate and store historical data
    historical_data = generator.generate_historical_data(days)
    generator.store_historical_data(session, historical_data)

    # Generate and store coupon payments
    coupon_payments = generator.generate_coupon_payments()
    generator.store_coupon_payments(session, coupon_payments)

    # Generate and store risk metrics
    risk_metrics = generator.generate_risk_metrics()
    generator.store_risk_metrics(session, risk_metrics)

    # Generate and store bond rating
    bond_rating = generator.generate_bond_rating()
    generator.store_bond_rating(session, bond_rating)

    print(f"Bond data successfully created and stored for ISIN: {isin}")
