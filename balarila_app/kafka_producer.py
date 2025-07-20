import json
from kafka import KafkaProducer
from django.conf import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

def send_kafka_event(topic, payload):
    """
    Send a message to a Kafka topic.
    
    :param topic: The Kafka topic to send the message to.
    :param payload: The message payload (should be JSON serializable).
    """
    try:
        producer.send(topic, payload)
        producer.flush() 
    except Exception as e:
        print(f"Failed to send message to Kafka topic {topic}: {e}")