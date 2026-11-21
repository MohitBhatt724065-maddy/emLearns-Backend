
from rest_framework import serializers

from .models import Course, Module, Lesson


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "created_at"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "course", "title", "description", "order"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "module",
            "title",
            "description",
            "content",
            "order",
            "video_url",
            "is_published",
            "created_at",
            "image",
        ]
