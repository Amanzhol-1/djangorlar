from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.viewsets import ViewSet

from .models import Course


class IsUserTheOwner(BasePermission):
    """
    Custom permission to check if the user is the owner of the course.
    """

    message = "Forbidden! You are not the owner of this course."

    def has_object_permission(
        self,
        request: DRFRequest,
        view: ViewSet,
        obj: Course
    ) -> bool:
        """
        Check if the user is the courses owner

        Parameters:
        request: DRFRequest - The request object
        view: ViewSet - The view being accessed
        obj: Course - The course object being accessed

        Returns:
        bool - True if user is the owner, False otherwise
        """
        return obj.owner == request.user