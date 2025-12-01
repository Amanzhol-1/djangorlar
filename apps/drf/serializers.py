from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Course, Lesson


User = get_user_model()


class AuthorSerializer(serializers.Serializer):
    """
    Serializer for author info in course responses.
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        """
        Supports custom User with full_name or default first+last name fallback.
        """
        if hasattr(obj, "full_name"):
            return obj.full_name
        full = f"{obj.first_name} {obj.last_name}".strip()
        return full if full else obj.email


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating courses with author info and lessons count.
    """

    author = AuthorSerializer(source="owner", read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "author",
            "lessons_count",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """
        Create a new course with owner set from request.user.
        """
        user = self.context["request"].user
        validated_data["owner"] = user
        return super().create(validated_data)


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a course.
    """

    author = AuthorSerializer(source="owner", read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "author",
            "lessons_count",
            "is_active",
            "created_at",
            "updated_at",
        ]


class CourseUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for full update (PUT) of a course.
    """

    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "is_active",
        ]


class LessonListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating lessons.
    """

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content",
            "order",
            "indentation",
            "is_published",
            "course",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order",
            "indentation",
            "is_published",
            "course",
            "created_at",
            "updated_at",
        ]


class LessonDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a lesson.
    """

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content",
            "order",
            "indentation",
            "is_published",
            "course",
            "created_at",
            "updated_at",
        ]