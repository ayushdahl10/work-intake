from django.conf import settings
from django.db import transaction
from utils.ai_service import BaseAIService

from external.agent.mock import MockAIService
from external.agent.ollama import OllamaAIService
from external.models import Status, WorkItem

SYSTEM_PROMPT = """
You are an AI work intake system. Analyze the provided ticket title and description.
Categorize, prioritize, summarize, and suggest next actions.

You MUST return ONLY a valid JSON object matching this schema:
{
  "category": "Bug Report" | "Billing Issue" | "Access Request" | "Feature Request" | "General Inquiry",
  "priority": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "summary": "1-2 sentence concise summary",
  "recommendedAction": "1 sentence next step for operators"
}
"""


def _claim_work(work_item_id) -> WorkItem:
    with transaction.atomic():
        wt_instance: WorkItem = (
            WorkItem.objects.select_for_update()
            .filter(pk=work_item_id, status__in=[Status.RECEIVED, Status.FAILED])
            .first()
        )
        if wt_instance:
            is_retry = wt_instance.status == Status.FAILED
            if wt_instance.check_transition_to(Status.ANALYSING):
                wt_instance.status = Status.ANALYSING
                if is_retry:
                    retry_count = wt_instance.retryCount + 1
                    wt_instance.retryCount = retry_count
                wt_instance.save()
                return wt_instance
            print(f"Cannot transition from {wt_instance.status} to {Status.ANALYSING}")
        return None


def _finalize_work(work_item_id, analysis_results):
    with transaction.atomic():
        wt_instance: WorkItem = (
            WorkItem.objects.select_for_update()
            .filter(pk=work_item_id, status=Status.ANALYSING)
            .first()
        )
        if wt_instance:
            if analysis_results.type == "Error":
                wt_instance.analysisError = analysis_results.message
                if wt_instance.check_transition_to(Status.FAILED):
                    wt_instance.status = Status.FAILED
                    wt_instance.save()
                    return
                print(f"Cannot transition from {wt_instance.status} to {Status.FAILED}")
            wt_instance.analysisResult = analysis_results.message
            if wt_instance.check_transition_to(Status.READY_FOR_REVIEW):
                wt_instance.status = Status.READY_FOR_REVIEW
                wt_instance.analysisError = None
                wt_instance.save()
            print(
                f"Cannot transition from {wt_instance.status} to {Status.READY_FOR_REVIEW}"
            )


# print can be changed to logger for keeping track of the analysis
def analysis_in_background(work_item_id):
    print(f"Running LLM analysis for work item {work_item_id} in background...")
    wt_instance = _claim_work(work_item_id)

    if not wt_instance:
        return

    provider = _get_ai_provider()
    analysis_results = provider.analyze_work_item(
        system_prompt=SYSTEM_PROMPT,
        title=wt_instance.title,
        description=wt_instance.description,
    )
    print(
        f"Running LLM analysis for work item {analysis_results.message} in background..."
    )
    _finalize_work(work_item_id, analysis_results)
    print(f"Running LLM analysis for work item {work_item_id} in background...")


def _get_ai_provider() -> BaseAIService:
    use_model = settings.AI_PROVIDER
    print(f"Using AI provider: {use_model}")
    if use_model == "mock":
        return MockAIService()
    elif use_model == "llama":
        return OllamaAIService()
