# Balarila Model

This project provides a GraphQL and REST API for grammar and spelling correction of Filipino text, leveraging an advanced deep learning model (Balarila GEC). It supports both synchronous and asynchronous grammar checking via Celery tasks.

- **Django Service (Balarila Model API)**
  - Hosts the Balarila grammar model. It accepts internal requests from the Spring Boot service, performs grammar correction on Filipino sentences, and returns the results.
- **Celery (Python Task Queue)**
  - Handles asynchronous requests using Kafka as a broker to establish communication between clients and workers.

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,django,tensorflow,pytorch,kafka,docker" />
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

### 3. Run Django Development Server

```bash
python manage.py runserver
```

### 4. Run Celery Worker

```bash
# This start a worker that will handle the asynchronous requests
celery -A balarila_api worker -l info
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
```
