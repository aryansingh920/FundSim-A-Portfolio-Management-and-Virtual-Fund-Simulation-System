from kafka import KafkaConsumer
import json
from asset_service.database import store_assets_in_db
import pandas as pd


class AssetConsumer:
    def __init__(self, topic_name, asset_type, kafka_server="localhost:9092"):
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=kafka_server,
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )
        self.asset_type = asset_type

    def consume(self):
        print(
            f"Listening for messages on topic '{self.consumer.subscription()}'.")
        for message in self.consumer:
            print(f"Consumed message: {message.value}")
            print(
                f"Metadata: Topic={message.topic}, Partition={message.partition}, Offset={message.offset}")
            data = [message.value]  # Wrap the message in a list
            df = pd.DataFrame(data)
            store_assets_in_db(df, self.asset_type)
            print(f"Stored data in {self.asset_type}.db successfully.")
