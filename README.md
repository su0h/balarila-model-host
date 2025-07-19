# Balarila Model

This project provides a GraphQL and REST API for grammar and spelling correction of Filipino text, leveraging an advanced deep learning model (Balarila GEC). It supports both synchronous and asynchronous grammar checking. Asynchronous processing is powered by Kafka as the message broker for scalability and resilience.

- **Django Service (Balarila Model API)**
  - Hosts the Balarila — grammar error correction model and exposes GraphQL endpoints. It accepts internal requests from the Spring Boot service, performs grammar correction on Filipino sentences, and returns the results.
- **Kafka (Message Broker)**
  - Manages the dispatch and processing of asynchronous grammar correction tasks.

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,django,graphql,tensorflow,pytorch,kafka,docker" />
  </a>
</p>

## Running the Application

The following commands are executed using a bash terminal:

### 1. Initial Setup

```bash
# If there is no virtual environment yet:
python3.7 -m venv .venv
pip install -r requirements.txt
```

### 2. Start Python Virtual Environment

```bash
# If there is already an existing virtual environment
source .venv/bin/activate
```

### 3. Start Kafka and Zookeeper

```bash
docker-compose up -d # start
```

### 4. Run Django Development Server and Kafka Consumer

```bash
# Run these two commands in separate terminals
python manage.py kafka_consumer # (1)
python manage.py runserver
```

## API Usage

To interact with the API, GraphQL was used for both synchronous and asynchronous calls

```graphql
# Example of a synchronous call to perform grammar check
query SynchronousGrammarCheck {
  checkGrammar(text: "Kain ka ba ng adobo") {
    originalText
    correctedText
    tags
    correctionsCount
  }
}

# Example of an asynchronous call
mutation {
  initiateGrammarCheckAsync(text: "Kain ka ba ng adobo") {
    correlationId
  }
}

# Get result of asynchronous call
query {
  getAsyncTaskResult(correlationId: "<produced_correlation_id>") {
    status
    ready
    result
  }
}
```
