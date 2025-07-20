from django.db import models

class GrammarResult(models.Model):
    """
    Model to store the results of grammar checks and corrections.
    """
    correlation_id = models.CharField(max_length=255, unique=True)
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='PENDING')
    result = models.JSONField(null=True, blank=True)  # Store result as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GrammarResult(correlation_id={self.correlation_id}, task_id={self.task_id})"