from rest_framework.decorators import api_view
from rest_framework.response import Response
from celery.result import AsyncResult

@api_view(['GET'])
def get_async_task_result(request, task_id):
    task = AsyncResult(task_id)
    if task.ready():
        status = task.status
        result = task.result # This will be the dictionary returned by the Celery task
        return Response({
            'task_id': task_id,
            'status': status,
            'result': result,
            'ready': True
        })
    else:
        return Response({
            'task_id': task_id,
            'status': task.status,
            'result': None,
            'ready': False
        })