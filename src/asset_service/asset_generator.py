import random
import pandas as pd
from faker import Faker
from .shares import generate_shares
from .bonds import generate_bonds
from .commodities import generate_commodities
from .loan import generate_loans

fake = Faker()


def generate_random_assets(num_assets):
    assets = []

    for _ in range(num_assets):
        asset_type = random.choice(["share", "bond", "commodity"])
        if asset_type == "share":
            assets.append(generate_shares())
        elif asset_type == "bond":
            assets.append(generate_bonds())
        elif asset_type == "commodity":
            assets.append(generate_commodities())
        elif asset_type == "loan":
            assets.append(generate_loans())

    return pd.DataFrame(assets)
