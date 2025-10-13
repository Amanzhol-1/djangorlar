# Python modules
from typing import Optional, Sequence

# Django modules
from django.contrib.admin import ModelAdmin, register
from django.core.handlers.wsgi import WSGIRequest

# Project modules
from apps.tasks.models import Task, UserTask, Project


@register(Project)
class ProjectAdmin(ModelAdmin):
    """
    Project admin configuration class.
    """

    list_display = (
        "id",
        "name",
        "author",
        "created_at"
    )
    list_display_links = (
        "id",
    )
    list_per_page = 50
    search_fields = (
        "id",
        "name",
    )
    ordering = (
        "-updated_at",
    )
    list_filter = (
        # "author",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
    filter_horizontal = (
        "users",
    )
    save_on_top = True
    fieldsets = (
        (
            "Project Information",
            {
                "fields": (
                    "name",
                    "author",
                    "users",
                )
            }
        ),
        (
            "Date and Time Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            }
        )
    )

    def has_add_permission(self, request: WSGIRequest) -> bool:
        """Disable add permission."""
        return False

    def has_delete_permission(self, request: WSGIRequest, obj: Optional[Project] = None) -> bool:
        """Disable delete permission."""
        return False

    def has_change_permission(self, request: WSGIRequest, obj: Optional[Project] = None) -> bool:
        """Disable change permission."""
        return False

    # def has_module_permission(self, request: WSGIRequest) -> bool:
    #     """Disable module permission."""
    #     return False


@register(Task)
class TaskAdmin(ModelAdmin):
    """
    Task admin configuration class.
    """
    list_display = (
        "id",
        "name",
        "project",
        "status_label",
        "created_at",
    )
    list_display_links = ("id",)
    list_per_page = 50
    search_fields = ("id", "name", "project__name")
    ordering = ("-updated_at",)
    list_filter = ("status", "project", "updated_at")

    readonly_fields = ("created_at", "updated_at", "deleted_at")
    save_on_top = True
    fieldsets = (
        (
            "Task Information",
            {
                "fields": (
                    "name",
                    "project",
                    "status",
                    "parent",
                )
            },
        ),
        (
            "Date and Time Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )

    def status_label(self, obj: Task) -> str:
        return obj.get_status_display()
    status_label.short_description = "Status"

    # def has_add_permission(self, request: WSGIRequest) -> bool: return False
    # def has_delete_permission(self, request: WSGIRequest, obj: Optional[Task] = None) -> bool: return False
    # def has_change_permission(self, request: WSGIRequest, obj: Optional[Task] = None) -> bool: return False


@register(UserTask)
class UserTaskAdmin(ModelAdmin):
    """
    UserTask admin configuration class.
    """
    list_display = (
        "id",
        "task",
        "user",
        "created_at",
    )
    list_display_links = ("id",)
    list_per_page = 50
    search_fields = ("id", "task__name", "user__username", "user__email")
    ordering = ("-updated_at",)
    list_filter = ("task__project", "updated_at")

    readonly_fields = ("created_at", "updated_at", "deleted_at")
    save_on_top = True
    fieldsets = (
        (
            "Assignment",
            {
                "fields": (
                    "task",
                    "user",
                )
            },
        ),
        (
            "Date and Time Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )

    # def has_add_permission(self, request: WSGIRequest) -> bool: return False
    # def has_delete_permission(self, request: WSGIRequest, obj: Optional[UserTask] = None) -> bool: return False
    # def has_change_permission(self, request: WSGIRequest, obj: Optional[UserTask] = None) -> bool: return False
