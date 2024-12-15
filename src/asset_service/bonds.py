import random
from faker import Faker

fake = Faker()


def generate_bonds():
    return {
        "asset_id": fake.uuid4(),
        "name": fake.company() + " Bond",
        "type": "bond",
        "face_value": 1000,
        "coupon_rate": round(random.uniform(1.0, 10.0), 2),
        "maturity_years": random.randint(1, 30),
        "credit_rating": random.choice(["AAA", "AA", "A", "BBB", "BB", "Junk"]),
        "price": round(random.uniform(800, 1100), 2)
    }
