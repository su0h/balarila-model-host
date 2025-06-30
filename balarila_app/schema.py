# corrector/schema.py
import graphene
from .utils import check_grammar, correct_grammar
from .tasks import check_grammar_async, correct_grammar_async
from celery.result import AsyncResult # For getting async task status/results
import json # For JSONString

class BalarilaCorrectionType(graphene.ObjectType):
    original_text = graphene.String()
    corrected_text = graphene.String()
    tags = graphene.List(graphene.String)
    corrections_count = graphene.Int()

class AsyncResultType(graphene.ObjectType):
    task_id = graphene.String()
    status = graphene.String()
    result = graphene.JSONString() # Use JSONString for flexible result data
    ready = graphene.Boolean()

    def resolve_status(self, info):
        task = AsyncResult(self.task_id)
        return task.status

    def resolve_result(self, info):
        task = AsyncResult(self.task_id)
        if task.ready():
            # Celery results are stored as Python objects, need to serialize to JSON string
            # Ensure the result (Python dict) is JSON-serializable
            return json.dumps(task.result)
        return None

    def resolve_ready(self, info):
        task = AsyncResult(self.task_id)
        return task.ready


class Query(graphene.ObjectType):
    checkGrammar = graphene.Field(BalarilaCorrectionType, text=graphene.String(required=True))
    correctGrammar = graphene.String(text=graphene.String(required=True))
    getAsyncTaskResult = graphene.Field(AsyncResultType, task_id=graphene.String(required=True))

    def resolve_checkGrammar(self, info, text):
        return check_grammar(text)

    def resolve_correctGrammar(self, info, text):
        return correct_grammar(text)

    def resolve_getAsyncTaskResult(self, info, task_id):
        # AsyncResultType object will resolve its own fields (status, result, ready)
        # by looking up the task_id in the Celery result backend.
        return AsyncResultType(task_id=task_id)


class InitiateGrammarCheckAsync(graphene.Mutation):
    class Arguments:
        text = graphene.String(required=True)
        correlation_id = graphene.String(required=False)

    task_id = graphene.String()

    @staticmethod
    def mutate(root, info, text, correlation_id=None):
        task = check_grammar_async.delay(text, correlation_id)
        return InitiateGrammarCheckAsync(task_id=task.id)

class InitiateGrammarCorrectionAsync(graphene.Mutation):
    class Arguments:
        text = graphene.String(required=True)
        correlation_id = graphene.String(required=False)

    task_id = graphene.String()

    @staticmethod
    def mutate(root, info, text, correlation_id=None):
        task = correct_grammar_async.delay(text, correlation_id)
        return InitiateGrammarCorrectionAsync(task_id=task.id)

class Mutation(graphene.ObjectType):
    initiateGrammarCheckAsync = InitiateGrammarCheckAsync.Field()
    initiateGrammarCorrectionAsync = InitiateGrammarCorrectionAsync.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)