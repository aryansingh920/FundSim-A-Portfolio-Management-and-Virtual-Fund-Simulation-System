from sqlalchemy import create_engine
import os

# Define the database directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "../../data/assets")
os.makedirs(TARGET_DIR, exist_ok=True)  # Ensure the directory exists


def store_assets_in_db(dataframe, asset_type):
    """
    Store assets in a database specific to the asset type.
    :param dataframe: The DataFrame containing the asset data.
    :param asset_type: The type of asset (e.g., shares, bonds, commodities).
    """
    # Define database path based on asset type
    db_name = f"{asset_type}.db"
    db_path = os.path.join(TARGET_DIR, db_name)
    DATABASE_URL = f"sqlite:///{db_path}"

    # Create database engine
    engine = create_engine(DATABASE_URL)

    # Store the data in the database (table name: 'assets')
    print(f"Storing {asset_type} in {db_name}...")
    dataframe.to_sql("assets", con=engine, if_exists="replace", index=False)
    print(f"{asset_type.capitalize()} stored successfully in {db_name}.")
