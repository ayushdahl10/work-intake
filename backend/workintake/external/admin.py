# Register your models here.
from django.contrib import admin

from external.models import WorkItem


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "external_id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("external_id", "title", "description")

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False
