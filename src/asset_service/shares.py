import random
from faker import Faker

fake = Faker()


def generate_shares():
    return {
        "asset_id": fake.uuid4(),
        "name": fake.company(),
        "type": "share",
        "sector": random.choice(["Tech", "Finance", "Energy", "Healthcare"]),
        "price": round(random.uniform(10, 500), 2),
        "volatility": round(random.uniform(0.1, 5.0), 2),
        "historical_return": round(random.uniform(-0.1, 0.2), 4)
    }
