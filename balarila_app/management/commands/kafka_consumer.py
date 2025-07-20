import json
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from balarila_app.models import GrammarResult
from balarila_app.utils import check_grammar

class Command(BaseCommand):
    help = 'Run Kafka consumer for grammar checking'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            'grammar-check',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='grammar-check-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )

        self.stdout.write(self.style.SUCCESS('Kafka consumer started...'))

        for message in consumer:
            data = message.value
            text = data.get('text')
            correlation_id = data.get('correlation_id')

            if not correlation_id or not text:
                continue

            # Run grammar check
            result = check_grammar(text)

            # Save result to DB for async retrieval
            GrammarResult.objects.update_or_create(
                correlation_id=correlation_id,
                defaults={'result': result}
            )

            self.stdout.write(f"Processed message with correlation_id={correlation_id}")
