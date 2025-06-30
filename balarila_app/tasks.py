# corrector/tasks.py
from celery import shared_task
from .utils import check_grammar, correct_grammar
from kafka import KafkaProducer
import json
import os
from django.conf import settings

# Initialize Kafka Producer globally or lazily.
# It's better to initialize it when the task first runs or through a Celery signal.
# For simplicity, we'll initialize it directly here, but be aware of connection management in production.
_kafka_producer = None

def get_kafka_producer():
    global _kafka_producer
    if _kafka_producer is None:
        # Get Kafka broker list from settings or default
        kafka_brokers = getattr(settings, 'CELERY_BROKER_URL', 'kafka://localhost:9092')
        # Extract just the host:port part(s)
        brokers = kafka_brokers.replace('kafka://', '').split(',')
        _kafka_producer = KafkaProducer(
            bootstrap_servers=brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Kafka Producer initialized for brokers: {brokers}")
    return _kafka_producer


@shared_task(bind=True)
def check_grammar_async(self, text, correlation_id=None):
    print(f"[{self.request.id}] Processing async grammar check for: {text[:50]}...")
    result_data = check_grammar(text)
    print(f"[{self.request.id}] Async grammar check complete. Corrections: {result_data['corrections_count']}")

    # Optionally, push results directly to a Kafka topic for Spring Boot to consume
    if correlation_id:
        try:
            producer = get_kafka_producer()
            message = {
                "task_id": self.request.id,
                "correlation_id": correlation_id,
                "status": "SUCCESS",
                "result": result_data # The actual correction data
            }
            # Use a specific topic for results, e.g., 'grammar_results_topic'
            producer.send('grammar_results_topic', message).get(timeout=30)
            print(f"[{self.request.id}] Sent result to Kafka topic 'grammar_results_topic'.")
        except Exception as e:
            print(f"[{self.request.id}] Error sending result to Kafka: {e}")

    return result_data # This result is stored in the CELERY_RESULT_BACKEND (django-db)


@shared_task(bind=True)
def correct_grammar_async(self, text, correlation_id=None):
    print(f"[{self.request.id}] Processing async grammar correction for: {text[:50]}...")
    corrected_text = correct_grammar(text)
    result_data = {"original_text": text, "corrected_text": corrected_text}

    # Optionally, push results directly to a Kafka topic
    if correlation_id:
        try:
            producer = get_kafka_producer()
            message = {
                "task_id": self.request.id,
                "correlation_id": correlation_id,
                "status": "SUCCESS",
                "result": result_data
            }
            producer.send('grammar_results_topic', message).get(timeout=30)
            print(f"[{self.request.id}] Sent correction result to Kafka topic 'grammar_results_topic'.")
        except Exception as e:
            print(f"[{self.request.id}] Error sending correction result to Kafka: {e}")

    return result_data