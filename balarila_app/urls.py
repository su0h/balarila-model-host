from django.urls import path
from . import views

urlpatterns = [
    path('async-result/<str:task_id>/', views.get_async_task_result, name='get_async_task_result'),
]