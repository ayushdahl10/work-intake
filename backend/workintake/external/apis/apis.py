from concurrent.futures import ThreadPoolExecutor

from django.db import IntegrityError, transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from external.filters import WorkItemFilter
from external.models import Status, WorkItem
from external.serializers import CreateWorkItemSerializer, ListWorkItemSerializer
from external.services import analysis_in_background

worker = ThreadPoolExecutor(max_workers=5)


@extend_schema(
    operation_id="create_work_item",
    summary="Create a work item",
    description="Creates a work item.",
    request=CreateWorkItemSerializer,
    responses={201: CreateWorkItemSerializer, 409: None},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def create_work_item(request):
    serializer = CreateWorkItemSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    try:
        with transaction.atomic():
            serializer.save()
            transaction.on_commit(
                lambda: worker.submit(analysis_in_background, serializer.instance.pk)
            )
    except IntegrityError:
        return Response(
            {"detail": "A work item with this external_id already exists."},
            status=status.HTTP_409_CONFLICT,
        )
    return Response(status=status.HTTP_201_CREATED, data=serializer.data)


@extend_schema(
    operation_id="get_work_items",
    summary="Get work items",
    description="Retrieves a list of work items or a specific work item by uid.",
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            enum=[status.value for status in Status],
            description="Filter work items by status.",
        ),
    ],
    responses={200: ListWorkItemSerializer(many=True), 404: None},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_work_item(request, **kwargs):
    uid = kwargs.get("uid")
    if uid:
        work_items = WorkItem.objects.filter(is_active=True, uid=uid).first()
        if not work_items:
            return Response(
                {"detail": "Work item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ListWorkItemSerializer(work_items)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        work_items = WorkItem.objects.filter(is_active=True).order_by("-created_at")
        work_items = WorkItemFilter(request.GET, queryset=work_items)
        serializer = ListWorkItemSerializer(work_items.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="retry_and_analyze_work_item",
    summary="Retry and analyze a work item",
    description="Retries a work item and analyzes it.",
    request=None,
    responses={200: None, 404: None},
)
@api_view(["PATCH"])
@permission_classes([AllowAny])
def retry_and_analyze_work_item(request, **kwargs):
    uid = kwargs.get("uid")
    if not uid:
        return Response(
            {"detail": "Work item uid is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    work_item = WorkItem.objects.filter(
        is_active=True, uid=uid, status__in=[Status.FAILED, Status.RECEIVED]
    ).first()
    if not work_item:
        return Response(
            {"detail": "Work item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    worker.submit(analysis_in_background, work_item.pk)
    return Response(status=status.HTTP_202_ACCEPTED, data="Analysis started")


@extend_schema(
    operation_id="complete_work_item",
    summary="Complete a work item",
    description="Marks a work item as completed.",
    request=None,
    responses={200: None, 404: None},
)
@api_view(["PATCH"])
@permission_classes([AllowAny])
def complete_work_item(request, **kwargs):
    uid = kwargs.get("uid")
    if not uid:
        return Response(
            {"detail": "Work item uid is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    with transaction.atomic():
        work_item = (
            WorkItem.objects.select_for_update()
            .filter(is_active=True, uid=uid, status=Status.READY_FOR_REVIEW)
            .first()
        )
        if not work_item:
            return Response(
                {
                    "detail": "Please make sure the selected work is in READY_FOR_REVIEW state."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if work_item.check_transition_to(Status.COMPLETED):
            work_item.status = Status.COMPLETED
            work_item.save()
        else:
            return Response(
                {
                    "detail": f"Cannot transition from {work_item.status} to {Status.COMPLETED}"
                }
            )
    return Response(status=status.HTTP_200_OK, data=work_item.uid)
