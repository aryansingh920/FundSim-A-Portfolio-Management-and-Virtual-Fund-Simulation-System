import random
import string
from datetime import datetime, timedelta
from typing import Tuple, Set

from faker import Faker
from sqlalchemy.orm import Session
from assets.bonds.model import (
    Bond, CouponPayment, BondRiskMetrics, BondRating, BondHistoricalData,
    BondIntradayData, Issuer
)


class BondDataInitializer:
    def __init__(self):
        """
        Initialize the bond data generator with tracking sets and faker
        """
        self.generated_isins: Set[str] = set()
        self.fake = Faker()

    def generate_unique_isin(self) -> str:
        """
        Generate a unique ISIN (International Securities Identification Number)

        Returns:
            str: A unique ISIN
        """
        while True:
            isin = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=12))
            if isin not in self.generated_isins:
                self.generated_isins.add(isin)
                return isin

    def generate_unique_cusip(self) -> str:
        """
        Generate a unique CUSIP (US bond identifier)

        Returns:
            str: A unique CUSIP
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

    def generate_bond_type(self) -> str:
        """
        Randomly select a bond type.

        Returns:
            str: Bond type
        """
        return random.choice(["Corporate", "Government", "Municipal", "Treasury", "Agency"])

    def generate_coupon_frequency(self) -> str:
        """
        Randomly select a coupon payment frequency.

        Returns:
            str: Coupon frequency
        """
        return random.choice(["Annual", "Semi-Annual", "Quarterly", "Monthly"])

    def generate_issuer(self) -> Issuer:
        """
        Generate a random issuer.

        Returns:
            Issuer: An Issuer object
        """
        name = self.fake.company()
        sector = random.choice(
            ["Technology", "Finance", "Healthcare", "Government", "Energy"])
        country = self.fake.country()
        return Issuer(name=name, sector=sector, country=country)

    def generate_bond(self, issuer: Issuer) -> Bond:
        """
        Generate a random bond with logical attributes.

        Args:
            issuer (Issuer): Issuer of the bond

        Returns:
            Bond: A Bond object
        """
        isin = self.generate_unique_isin()
        cusip = self.generate_unique_cusip()
        bond_name = f"{issuer.name} {random.randint(2025, 2035)} Bond"
        issue_date = self.fake.date_between(start_date="-10y", end_date="-1y")
        maturity_date = self.fake.date_between(
            start_date="+1y", end_date="+30y")
        coupon_rate = round(random.uniform(0.5, 10), 2)
        coupon_frequency = self.generate_coupon_frequency()
        face_value = round(random.uniform(100, 10000), 2)
        bond_type = self.generate_bond_type()
        currency = random.choice(["USD", "EUR", "GBP", "JPY"])
        callable = random.choice([0, 1])
        puttable = random.choice([0, 1])
        convertible = random.choice([0, 1])
        market = random.choice(["NYSE", "NASDAQ", "LSE", "JPX", "Euronext"])
        sector = issuer.sector

        return Bond(
            isin=isin,
            cusip=cusip,
            bond_name=bond_name,
            issuer=issuer,
            issue_date=issue_date,
            maturity_date=maturity_date,
            coupon_rate=coupon_rate,
            coupon_frequency=coupon_frequency,
            face_value=face_value,
            bond_type=bond_type,
            currency=currency,
            callable=callable,
            puttable=puttable,
            convertible=convertible,
            market=market,
            sector=sector
        )

    def generate_coupon_payment(self, bond: Bond) -> CouponPayment:
        """
        Generate a random coupon payment for a bond.

        Args:
            bond (Bond): Bond object

        Returns:
            CouponPayment: A CouponPayment object
        """
        payment_date = self.fake.date_between(
            start_date=bond.issue_date, end_date=bond.maturity_date)
        payment_amount = round(bond.face_value * bond.coupon_rate / 100, 2)

        return CouponPayment(
            isin=bond.isin,
            payment_date=payment_date,
            payment_amount=payment_amount
        )

    def generate_bond_risk_metrics(self, bond: Bond) -> BondRiskMetrics:
        """
        Generate random bond risk metrics.

        Args:
            bond (Bond): Bond object

        Returns:
            BondRiskMetrics: A BondRiskMetrics object
        """
        duration = round(random.uniform(1, 20), 2)
        modified_duration = round(duration * random.uniform(0.8, 1.2), 2)
        convexity = round(random.uniform(0.1, 5), 2)
        yield_to_maturity = round(random.uniform(0.5, 15), 2)
        current_yield = round(yield_to_maturity - random.uniform(0, 2), 2)
        spread_to_treasury = round(random.uniform(0, 5), 2)

        return BondRiskMetrics(
            isin=bond.isin,
            duration=duration,
            modified_duration=modified_duration,
            convexity=convexity,
            yield_to_maturity=yield_to_maturity,
            current_yield=current_yield,
            spread_to_treasury=spread_to_treasury
        )

    def generate_bond_rating(self, bond: Bond) -> BondRating:
        """
        Generate a random bond rating.

        Args:
            bond (Bond): Bond object

        Returns:
            BondRating: A BondRating object
        """
        rating_agency = random.choice(["S&P", "Moody's", "Fitch"])
        credit_rating = random.choice(
            ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"])
        outlook = random.choice(
            ["Stable", "Positive", "Negative", "Developing"])
        rating_date = self.fake.date_between(
            start_date=bond.issue_date, end_date="today")

        return BondRating(
            isin=bond.isin,
            rating_agency=rating_agency,
            credit_rating=credit_rating,
            outlook=outlook,
            rating_date=rating_date
        )

    def generate_historical_data(self, bond: Bond) -> BondHistoricalData:
        """
        Generate random historical data for a bond.

        Args:
            bond (Bond): Bond object

        Returns:
            BondHistoricalData: A BondHistoricalData object
        """
        date = self.fake.date_between(
            start_date=bond.issue_date, end_date="today")
        open_price = round(random.uniform(90, 110), 2)
        close_price = round(open_price * random.uniform(0.95, 1.05), 2)
        day_high = max(open_price, close_price) + \
            round(random.uniform(0, 5), 2)
        day_low = min(open_price, close_price) - round(random.uniform(0, 5), 2)
        trading_volume = random.randint(1000, 1000000)

        return BondHistoricalData(
            isin=bond.isin,
            date=date,
            open_price=open_price,
            close_price=close_price,
            day_high=day_high,
            day_low=day_low,
            trading_volume=trading_volume
        )

    def generate_intraday_data(self, bond: Bond) -> BondIntradayData:
        """
        Generate random intraday data for a bond.

        Args:
            bond (Bond): Bond object

        Returns:
            BondIntradayData: A BondIntradayData object
        """
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))
        price = round(random.uniform(90, 110), 2)
        volume = random.randint(1000, 100000)

        return BondIntradayData(
            isin=bond.isin,
            timestamp=timestamp,
            price=price,
            volume=volume
        )

    def generate_random_bond_data(self, session: Session):
        """
        Generate and persist random bond data with logical relationships.

        Args:
            session (Session): SQLAlchemy session for database operations
        """
        issuer = self.generate_issuer()
        session.add(issuer)
        session.commit()

        bond = self.generate_bond(issuer)
        session.add(bond)

        for _ in range(random.randint(1, 5)):
            session.add(self.generate_coupon_payment(bond))

        session.add(self.generate_bond_risk_metrics(bond))
        session.add(self.generate_bond_rating(bond))

        for _ in range(random.randint(5, 15)):
            session.add(self.generate_historical_data(bond))

        for _ in range(random.randint(5, 15)):
            session.add(self.generate_intraday_data(bond))

        session.commit()


if __name__ == "__main__":
    BondDataInitializer().generate_random_bond_data()
