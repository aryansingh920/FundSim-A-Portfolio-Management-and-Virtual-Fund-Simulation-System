# main.py
import time
import pandas as pd


from asset_service.shares import generate_shares
from asset_service.bonds import generate_bonds
from asset_service.commodities import generate_commodities
from asset_service.database import store_assets_in_db
from asset_service.loan import generate_loans
from kafka_service.kafka_producer import AssetProducer
from kafka_service.kafka_consumer import AssetConsumer


def kafka_produce():
    print("Generating assets individually...")
    producer = AssetProducer(topic_name="assets")

    # Generate shares
    num_shares = 5
    for _ in range(num_shares):
        share = generate_shares()
        producer.publish(share)

    # Generate bonds
    num_bonds = 3
    for _ in range(num_bonds):
        bond = generate_bonds()
        producer.publish(bond)

    # Generate commodities
    num_commodities = 2
    for _ in range(num_commodities):
        commodity = generate_commodities()
        producer.publish(commodity)

    # Generate loans
    num_loans = 4
    for _ in range(num_loans):
        loan = generate_loans()
        producer.publish(loan)

    print("All assets published to Kafka successfully!")

def create_assets():
    print("Generating assets individually...")

    # Generate shares
    num_shares = 40
    shares_data = [generate_shares() for _ in range(num_shares)]
    shares_df = pd.DataFrame(shares_data)
    print("Generated Shares:")
    print(shares_df)

    # Generate bonds
    num_bonds = 40
    bonds_data = [generate_bonds() for _ in range(num_bonds)]
    bonds_df = pd.DataFrame(bonds_data)
    print("Generated Bonds:")
    print(bonds_df)

    # Generate commodities
    num_commodities = 5
    commodities_data = [generate_commodities() for _ in range(num_commodities)]
    commodities_df = pd.DataFrame(commodities_data)
    print("Generated Commodities:")
    print(commodities_df)

    num_loans = 20
    loans_data = [generate_loans() for _ in range(num_loans)]
    loans_df = pd.DataFrame(loans_data)
    print("Generated Loans:")
    print(loans_df)

    # Store assets in individual databases
    print("Storing shares...")
    store_assets_in_db(shares_df, "shares")

    print("Storing bonds...")
    store_assets_in_db(bonds_df, "bonds")

    print("Storing commodities...")
    store_assets_in_db(commodities_df, "commodities")

    print("Storing loans...")
    store_assets_in_db(loans_df, "loans")

    print("All assets generated and stored successfully!")


def start_consumers():
    print("Starting consumers...")

    # Consumers for different asset types
    share_consumer = AssetConsumer(topic_name="assets", asset_type="shares")
    bond_consumer = AssetConsumer(topic_name="assets", asset_type="bonds")
    loan_consumer = AssetConsumer(topic_name="assets", asset_type="loans")
    commodity_consumer = AssetConsumer(
        topic_name="assets", asset_type="commodities")

    # Run consumers
    share_consumer.consume()
    bond_consumer.consume()
    loan_consumer.consume()
    commodity_consumer.consume()


def main():
    create_assets()
    kafka_produce()
    print("Waiting for messages...")
    time.sleep(10)
    start_consumers()
    return


if __name__ == "__main__":
    main()
