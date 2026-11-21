
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Course, Module, Lesson
from .serializers import (
    CourseSerializer,
    ModuleSerializer,
    LessonSerializer,
)


@api_view(["GET"])
def course_list(request):
    courses = Course.objects.all()
    
    search = request.query_params.get("search")
    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def module_list(request):
    modules = Module.objects.all()

    # Optional filtering by course ID
    course_id = request.query_params.get("course_id")

    if course_id:
        modules = modules.filter(course_id=course_id)
        
    search = request.query_params.get("search")
    
    if search:
        modules = modules.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
        
    

    serializer = ModuleSerializer(modules, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def lesson_list(request):
    lessons = Lesson.objects.all()

    module_id = request.query_params.get("module_id")
    course_id = request.query_params.get("course_id")
    search = request.query_params.get("search")

    if module_id:
        lessons = lessons.filter(module_id=module_id)

    if course_id:
        lessons = lessons.filter(module__course_id=course_id)

    if search:
        lessons = lessons.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(content__icontains=search)
        )

    serializer = LessonSerializer(lessons, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    serializer = CourseSerializer(course)

    return Response(serializer.data)

@api_view(["GET"])
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)

    serializer = ModuleSerializer(module)

    return Response(serializer.data)

@api_view(["GET"])
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    serializer = LessonSerializer(lesson)

    return Response(serializer.data)
