from rest_framework import serializers

from .models import Course, Module, Lesson, Enrollment, LessonProgress


def published_lessons(course):
    return Lesson.objects.filter(module__course=course, is_published=True)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = "__all__"

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(module=obj, is_published=True).order_by("order")
        return LessonSerializer(lessons, many=True, context=self.context).data


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lesson_count(self, obj):
        return published_lessons(obj).count()


class CourseDetailSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lesson_count(self, obj):
        return published_lessons(obj).count()

    def get_modules(self, obj):
        modules = Module.objects.filter(course=obj).order_by("order")
        return ModuleWithLessonsSerializer(modules, many=True, context=self.context).data

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=request.user, course=obj).exists()


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "enrolled_at",
            "total_lessons",
            "completed_lessons",
            "progress_percent",
            "next_lesson_id",
        ]

    def get_total_lessons(self, obj):
        return published_lessons(obj.course).count()

    def get_completed_lessons(self, obj):
        return LessonProgress.objects.filter(
            user=obj.user,
            completed=True,
            lesson__module__course=obj.course,
            lesson__is_published=True,
        ).count()

    def get_progress_percent(self, obj):
        total = self.get_total_lessons(obj)
        if total == 0:
            return 0
        return round(self.get_completed_lessons(obj) / total * 100)

    def get_next_lesson_id(self, obj):
        done_ids = LessonProgress.objects.filter(
            user=obj.user,
            completed=True,
            lesson__module__course=obj.course,
        ).values_list("lesson_id", flat=True)
        lesson = (
            published_lessons(obj.course)
            .exclude(id__in=done_ids)
            .order_by("module__order", "order")
            .first()
        )
        return lesson.id if lesson else None