import random
from faker import Faker

fake = Faker()


def generate_commodities():
    return {
        "asset_id": fake.uuid4(),
        "name": random.choice(["Gold", "Silver", "Oil", "Wheat", "Coffee"]),
        "type": "commodity",
        "price": round(random.uniform(50, 2000), 2),
        "historical_return": round(random.uniform(-0.05, 0.1), 4)
    }
