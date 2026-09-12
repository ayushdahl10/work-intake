from django_filters.rest_framework import FilterSet

from external.models import WorkItem


class WorkItemFilter(FilterSet):
    class Meta:
        model = WorkItem
        fields = ["status"]
