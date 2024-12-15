from kafka.producer import KafkaProducer
import json


class AssetProducer:
    def __init__(self, topic_name, kafka_server="localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_server,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        self.topic = topic_name

    def publish(self, message):
        self.producer.send(self.topic, value=message)
        print(f"Published message to topic '{self.topic}': {message}")
