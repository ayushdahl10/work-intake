from django.db import models
from utils.base_model import BaseModel

# Create your models here.


class Status(models.TextChoices):
    RECEIVED = "RECEIVED", "RECEIVED"
    ANALYSING = "ANALYSING", "ANALYSING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW", "READY_FOR_REVIEW"
    COMPLETED = "COMPLETED", "COMPLETED"
    FAILED = "FAILED", "FAILED"


ALLOWED_TRANSITIONS = {
    Status.RECEIVED: [Status.ANALYSING],
    Status.ANALYSING: [Status.READY_FOR_REVIEW, Status.FAILED],
    Status.READY_FOR_REVIEW: [Status.COMPLETED, Status.ANALYSING],
    Status.FAILED: [Status.ANALYSING],
    Status.COMPLETED: [],
}


class WorkItem(BaseModel):
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.RECEIVED
    )
    analysisResult = models.JSONField(null=True, blank=True)
    analysisError = models.TextField(null=True, blank=True)
    retryCount = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"

    def __str__(self):
        return self.title

    def check_transition_to(self, new_status: Status) -> bool:
        if new_status == self.status:
            return True
        valid_transitions = ALLOWED_TRANSITIONS[self.status]
        return new_status  in valid_transitions