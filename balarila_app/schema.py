# corrector/schema.py
import graphene
import uuid
import json

from balarila_app.models import GrammarResult
from .utils import check_grammar, correct_grammar
from .kafka_producer import send_kafka_event

class BalarilaCorrectionType(graphene.ObjectType):
    original_text = graphene.String()
    corrected_text = graphene.String()
    tags = graphene.List(graphene.String)
    corrections_count = graphene.Int()

class AsyncResultType(graphene.ObjectType):
    correlation_id = graphene.String()
    status = graphene.String()
    result = graphene.JSONString()
    ready = graphene.Boolean()

class Query(graphene.ObjectType):
    # Synchronous calls for grammar check and correction
    checkGrammar = graphene.Field(BalarilaCorrectionType, text=graphene.String(required=True))
    correctGrammar = graphene.String(text=graphene.String(required=True))

    # Asynchronous calls for grammar check and correction
    getAsyncTaskResult = graphene.Field(AsyncResultType, correlation_id=graphene.String(required=True))

    def resolve_checkGrammar(self, info, text):
        return check_grammar(text)

    def resolve_correctGrammar(self, info, text):
        return correct_grammar(text)

    def resolve_getAsyncTaskResult(self, info, correlation_id):
        try:
            result = GrammarResult.objects.get(correlation_id=correlation_id)
            return AsyncResultType(
                correlation_id=correlation_id,
                status="SUCCESS",
                ready=True,
                result=json.dumps(result.result)
            )
        except GrammarResult.DoesNotExist:
            return AsyncResultType(
                correlation_id=correlation_id,
                status="PENDING",
                ready=False,
                result=None
            )

class InitiateGrammarCheckAsync(graphene.Mutation):
    class Arguments:
        text = graphene.String(required=True)
    
    correlation_id = graphene.String(required=False)

    @staticmethod
    def mutate(self, info, text):
        cid = str(uuid.uuid4())
        send_kafka_event("grammar-check", {
            "text": text,
            "correlation_id": cid })
        return InitiateGrammarCheckAsync(correlation_id=cid)


class Mutation(graphene.ObjectType):
    initiateGrammarCheckAsync = InitiateGrammarCheckAsync.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)