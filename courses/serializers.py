from rest_framework import serializers

from .models import Course, Module, Lesson, Enrollment, LessonProgress


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


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "course", "title", "description", "order"]


class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ["id", "course", "title", "description", "order", "lessons"]

    def get_lessons(self, obj):
        lessons = obj.lessons.filter(is_published=True)
        return LessonSerializer(lessons, many=True, context=self.context).data


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "category",
            "level",
            "thumbnail",
            "lesson_count",
            "created_at",
            "updated_at",
        ]

    def get_lesson_count(self, obj):
        return Lesson.objects.filter(
            module__course=obj, is_published=True
        ).count()


class CourseDetailSerializer(CourseSerializer):
    modules = ModuleWithLessonsSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ["modules", "is_enrolled"]

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                user=request.user, course=obj
            ).exists()
        return False


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "enrolled_at",
            "total_lessons",
            "completed_lessons",
            "progress_percent",
        ]

    def get_total_lessons(self, obj):
        return Lesson.objects.filter(
            module__course=obj.course, is_published=True
        ).count()

    def get_completed_lessons(self, obj):
        return LessonProgress.objects.filter(
            user=obj.user,
            lesson__module__course=obj.course,
            lesson__is_published=True,
            completed=True,
        ).count()

    def get_progress_percent(self, obj):
        total = self.get_total_lessons(obj)
        if total == 0:
            return 0
        return round(self.get_completed_lessons(obj) / total * 100)