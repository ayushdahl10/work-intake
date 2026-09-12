from django.urls import path
from rest_framework.routers import SimpleRouter

from .apis import (
    complete_work_item,
    create_work_item,
    get_work_item,
    retry_and_analyze_work_item,
)

router = SimpleRouter()

urlpatterns = [
    path("create-work-item", create_work_item, name="create-work-item"),
    path("work-item", get_work_item, name="get-work-items"),
    path("work-item/<str:uid>", get_work_item, name="get-work-items"),
    path("work-item/<str:uid>/complete", complete_work_item, name="complete-work-item"),
    path(
        "work-item/<str:uid>/trigger",
        retry_and_analyze_work_item,
        name="retry-and-analyze-work-item",
    ),
]

urlpatterns += router.urls
