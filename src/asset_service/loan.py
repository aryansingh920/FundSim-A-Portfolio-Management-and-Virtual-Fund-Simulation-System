import random
from faker import Faker

fake = Faker()


def generate_loans():
    """
    Generate a random loan asset.
    """
    return {
        "asset_id": fake.uuid4(),
        "borrower_name": fake.name(),
        "type": "loan",
        # Loan amount
        "principal_amount": round(random.uniform(1000, 100000), 2),
        # Annual interest rate in %
        "interest_rate": round(random.uniform(3.0, 15.0), 2),
        "loan_term_years": random.randint(1, 30),  # Term in years
        "credit_score": random.randint(300, 850),  # Credit score (300-850)
        "repayment_frequency": random.choice(["monthly", "quarterly", "annually"]),
        # Outstanding balance
        "outstanding_amount": round(random.uniform(500, 95000), 2),
    }
