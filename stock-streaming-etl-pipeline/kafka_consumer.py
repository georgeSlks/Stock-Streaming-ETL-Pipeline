from kafka import KafkaConsumer
import json

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'TestTopic',
    bootstrap_servers='localhost:9092',  
    group_id='test-consumer-group',  # Consumer group ID
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialize the messages
)

# Consume messages from Kafka
def consume_messages():
    print("Consuming messages from Kafka topic 'TestTopic'...")

    # Infinite loop to keep consuming messages
    for message in consumer:
        # Print each consumed message (stock data from the producer)
        print(f"Received message: {message.value}")

if __name__ == "__main__":
    consume_messages()
