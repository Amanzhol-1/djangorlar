from typing import Any

from django.db import models
from django.db.models import Count, Q

from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Course, Lesson
from .serializers import CourseListSerializer, LessonListSerializer
from .permissions import IsUserTheOwner

COURSE_ERROR_NOT_FOUND = "Course not found"
COURSE_ALREADY_ACTIVE = "Course is already active"
COURSE_ALREADY_INACTIVE = "Course is already inactive"
COURSE_DELETED_SUCCESS = "Course deleted successfully"

LESSON_ERROR_NO_COURSES = "No courses found"
LESSON_ERROR_NOT_FOUND = "Lesson not found"
LESSON_ERROR_NOT_OWNER = "You are not the owner of this course"
LESSON_ERROR_TARGET_NOT_FOUND = "Target lesson not found in the same course"
LESSON_DELETED_SUCCESS = "Lesson deleted successfully"
LESSON_PUBLISHED_SUCCESS = "Lesson published successfully"
LESSON_UNPUBLISHED_SUCCESS = "Lesson unpublished successfully"

LESSON_NEW_ORDER_DEFAULT = 1
LESSON_INDENTATION_ROOT = 0


class CourseViewSet(ViewSet):
    """
    ViewSet for course endpoints
    """

    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        """
        Returns permissions for current action
        """
        if self.action in ("update", "partial_update", "destroy", "activate", "deactivate"):
            permission_classes = [IsAuthenticated, IsUserTheOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns queryset for courses with lessons_count
        """
        queryset = (
            Course.objects.filter(deleted_at__isnull=True)
            .select_related("owner")
            .annotate(
                lessons_count=Count(
                    "lessons",
                    filter=Q(lessons__deleted_at__isnull=True),
                )
            )
        )

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active_bool)

        return queryset

    def list(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        List courses with author and lessons count
        """
        queryset = self.get_queryset()
        serializer = CourseListSerializer(queryset, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def retrieve(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Retrieve single course by id
        """
        queryset = self.get_queryset()
        course = queryset.filter(id=pk).first()

        if not course:
            return DRFResponse({"detail": COURSE_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        serializer = CourseListSerializer(course)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def create(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Create course and set owner from request user
        """
        serializer = CourseListSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    def update(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Full update of course by id
        """
        queryset = self.get_queryset()
        course = queryset.filter(id=pk).first()

        if not course:
            return DRFResponse({"detail": COURSE_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        serializer = CourseListSerializer(
            instance=course,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def destroy(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Soft delete course by id
        """
        queryset = self.get_queryset()
        course = queryset.filter(id=pk).first()

        if not course:
            return DRFResponse({"detail": COURSE_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        course.delete()

        return DRFResponse({"detail": COURSE_DELETED_SUCCESS}, status=HTTP_204_NO_CONTENT)

    @action(
        methods=("POST",),
        detail=True,
        url_path="activate",
        url_name="activate",
        permission_classes=(IsAuthenticated, IsUserTheOwner),
    )
    def activate(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Activate inactive course
        """
        queryset = (
            Course.objects.filter(deleted_at__isnull=True)
            .select_related("owner")
            .annotate(
                lessons_count=Count(
                    "lessons",
                    filter=Q(lessons__deleted_at__isnull=True),
                )
            )
        )
        course = queryset.filter(id=pk).first()

        if not course:
            return DRFResponse({"detail": COURSE_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, course)

        if course.is_active:
            return DRFResponse({"detail": COURSE_ALREADY_ACTIVE}, status=HTTP_400_BAD_REQUEST)

        course.is_active = True
        course.save()

        serializer = CourseListSerializer(course)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(
        methods=("POST",),
        detail=True,
        url_path="deactivate",
        url_name="deactivate",
        permission_classes=(IsAuthenticated, IsUserTheOwner),
    )
    def deactivate(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Deactivate active course
        """
        queryset = (
            Course.objects.filter(deleted_at__isnull=True)
            .select_related("owner")
            .annotate(
                lessons_count=Count(
                    "lessons",
                    filter=Q(lessons__deleted_at__isnull=True),
                )
            )
        )
        course = queryset.filter(id=pk).first()

        if not course:
            return DRFResponse({"detail": COURSE_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, course)

        if not course.is_active:
            return DRFResponse({"detail": COURSE_ALREADY_INACTIVE}, status=HTTP_400_BAD_REQUEST)

        course.is_active = False
        course.save()

        serializer = CourseListSerializer(course)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(
        methods=("GET",),
        detail=True,
        url_path="lessons",
        url_name="lessons",
        permission_classes=(IsAuthenticated,),
    )
    def lessons(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        List non deleted lessons of course
        """
        queryset = Lesson.objects.filter(
            course_id=pk,
            deleted_at__isnull=True,
        )

        serializer = LessonListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return DRFResponse(serializer.data, status=HTTP_200_OK)


class LessonViewSet(ViewSet):
    """
    ViewSet for lesson endpoints
    """

    permission_classes = (IsAuthenticated, IsUserTheOwner)

    def _get_course_for_user(self, user: Any) -> Course | None:
        """
        Returns first non deleted course owned by user
        """
        return (
            Course.objects.filter(owner=user, deleted_at__isnull=True)
            .order_by("created_at")
            .first()
        )

    def _get_lesson_for_owner(self, pk: int, user: Any) -> Lesson | None:
        """
        Returns lesson by id if user owns its course
        """
        try:
            lesson = Lesson.objects.select_related("course__owner").get(
                id=pk,
                deleted_at__isnull=True,
            )
        except Lesson.DoesNotExist:
            return None

        if lesson.course.owner != user:
            return None

        return lesson

    def create(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Create lesson in first user course and put it on top
        """
        course = self._get_course_for_user(request.user)

        if not course:
            return DRFResponse({"detail": LESSON_ERROR_NO_COURSES}, status=HTTP_400_BAD_REQUEST)

        min_order = (
            Lesson.objects.filter(course=course, deleted_at__isnull=True)
            .aggregate(models.Min("order"))["order__min"]
        )

        if min_order is None:
            new_order = LESSON_NEW_ORDER_DEFAULT
        else:
            new_order = min_order - 1

        serializer = LessonListSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(order=new_order, course=course)

        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    @action(
        methods=("PUT",),
        detail=True,
        url_path="move",
        url_name="move",
        permission_classes=(IsAuthenticated, IsUserTheOwner),
    )
    def move(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Move lesson before target lesson or to the end
        """
        lesson = self._get_lesson_for_owner(pk, request.user)
        if not lesson:
            return DRFResponse({"detail": LESSON_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        before_lesson_id = request.data.get("before_lesson_id")

        course_lessons = (
            Lesson.objects.filter(
                course=lesson.course,
                deleted_at__isnull=True,
            )
            .exclude(id=lesson.id)
            .order_by("order")
        )

        if before_lesson_id is None:
            max_order = course_lessons.aggregate(models.Max("order"))["order__max"]
            if max_order is None:
                new_order = LESSON_NEW_ORDER_DEFAULT
            else:
                new_order = max_order + 1
            new_indentation = LESSON_INDENTATION_ROOT
        else:
            try:
                before_lesson = Lesson.objects.get(
                    id=before_lesson_id,
                    course=lesson.course,
                    deleted_at__isnull=True,
                )
            except Lesson.DoesNotExist:
                return DRFResponse(
                    {"detail": LESSON_ERROR_TARGET_NOT_FOUND},
                    status=HTTP_404_NOT_FOUND,
                )

            lessons_before = (
                course_lessons.filter(order__lt=before_lesson.order)
                .order_by("-order")
                .first()
            )

            if lessons_before is None:
                new_order = before_lesson.order - 1
                new_indentation = LESSON_INDENTATION_ROOT
            else:
                new_order = (lessons_before.order + before_lesson.order) / 2
                new_indentation = before_lesson.indentation

        lesson.order = new_order
        lesson.indentation = new_indentation
        lesson.save()

        return DRFResponse(
            {
                "order": float(lesson.order),
                "indentation": lesson.indentation,
            },
            status=HTTP_200_OK,
        )

    def destroy(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Soft delete lesson by id
        """
        lesson = self._get_lesson_for_owner(pk, request.user)
        if not lesson:
            return DRFResponse({"detail": LESSON_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        lesson.delete()

        return DRFResponse({"detail": LESSON_DELETED_SUCCESS}, status=HTTP_204_NO_CONTENT)

    @action(
        methods=("POST",),
        detail=True,
        url_path="publish",
        url_name="publish",
        permission_classes=(IsAuthenticated, IsUserTheOwner),
    )
    def publish_lesson(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Publish lesson
        """
        lesson = self._get_lesson_for_owner(pk, request.user)
        if not lesson:
            return DRFResponse({"detail": LESSON_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        lesson.is_published = True
        lesson.save()

        return DRFResponse({"detail": LESSON_PUBLISHED_SUCCESS}, status=HTTP_200_OK)

    @action(
        methods=("POST",),
        detail=True,
        url_path="unpublish",
        url_name="unpublish",
        permission_classes=(IsAuthenticated, IsUserTheOwner),
    )
    def unpublish_lesson(
        self,
        request: DRFRequest,
        pk: int | None = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Unpublish lesson
        """
        lesson = self._get_lesson_for_owner(pk, request.user)
        if not lesson:
            return DRFResponse({"detail": LESSON_ERROR_NOT_FOUND}, status=HTTP_404_NOT_FOUND)

        lesson.is_published = False
        lesson.save()

        return DRFResponse({"detail": LESSON_UNPUBLISHED_SUCCESS}, status=HTTP_200_OK)