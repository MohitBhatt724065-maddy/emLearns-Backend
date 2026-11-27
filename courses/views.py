from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course, Module, Lesson, Enrollment, LessonProgress
from .serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    ModuleSerializer,
    LessonSerializer,
    EnrollmentSerializer,
)


# ---------- Public (read-only) ----------

@api_view(["GET"])
def course_list(request):
    courses = Course.objects.filter(is_published=True)

    search = request.query_params.get("search")
    if search:
        courses = courses.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    category = request.query_params.get("category")
    if category:
        courses = courses.filter(category__iexact=category)

    serializer = CourseSerializer(courses, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    serializer = CourseDetailSerializer(course, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def module_list(request):
    modules = Module.objects.filter(course__is_published=True)

    course_id = request.query_params.get("course_id")
    if course_id:
        modules = modules.filter(course_id=course_id)

    search = request.query_params.get("search")
    if search:
        modules = modules.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    serializer = ModuleSerializer(modules, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk, course__is_published=True)
    serializer = ModuleSerializer(module, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def lesson_list(request):
    lessons = Lesson.objects.filter(
        is_published=True, module__course__is_published=True
    )

    module_id = request.query_params.get("module_id")
    course_id = request.query_params.get("course_id")
    search = request.query_params.get("search")

    if module_id:
        lessons = lessons.filter(module_id=module_id)

    if course_id:
        lessons = lessons.filter(module__course_id=course_id)

    if search:
        lessons = lessons.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(content__icontains=search)
        )

    serializer = LessonSerializer(lessons, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def lesson_detail(request, pk):
    lesson = get_object_or_404(
        Lesson, pk=pk, is_published=True, module__course__is_published=True
    )
    serializer = LessonSerializer(lesson, context={"request": request})
    return Response(serializer.data)


# ---------- Logged-in actions ----------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enroll(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )
    serializer = EnrollmentSerializer(enrollment, context={"request": request})
    return Response(serializer.data, status=201 if created else 200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_enrollments(request):
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related("course")
    serializer = EnrollmentSerializer(
        enrollments, many=True, context={"request": request}
    )
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_lesson(request, pk):
    lesson = get_object_or_404(
        Lesson, pk=pk, is_published=True, module__course__is_published=True
    )
    course = lesson.module.course

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return Response(
            {"detail": "You must enroll in this course first."}, status=403
        )

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson
    )
    if not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

    return Response(
        {
            "lesson": lesson.id,
            "completed": True,
            "completed_at": progress.completed_at,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_progress(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)

    completed_ids = list(
        LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=course,
            lesson__is_published=True, 
            completed=True,
        ).values_list("lesson_id", flat=True)
    )
    total = Lesson.objects.filter(
        module__course=course, is_published=True
    ).count()

    return Response(
        {
            "course": course.id,
            "completed_lesson_ids": completed_ids,
            "completed_lessons": len(completed_ids),
            "total_lessons": total,
            "progress_percent": round(len(completed_ids) / total * 100) if total else 0,
        }
    )