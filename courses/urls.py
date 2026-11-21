from django.urls import path

from .views import (
    course_list,
    course_detail,
    module_list,
    module_detail,
    lesson_list,
    lesson_detail,
    enroll,
    my_enrollments,
    complete_lesson,
    course_progress,
)


urlpatterns = [
    path("courses/", course_list, name="course-list"),
    path("courses/<int:pk>/", course_detail, name="course-detail"),
    path("courses/<int:pk>/enroll/", enroll, name="course-enroll"),
    path("courses/<int:pk>/progress/", course_progress, name="course-progress"),

    path("modules/", module_list, name="module-list"),
    path("modules/<int:pk>/", module_detail, name="module-detail"),

    path("lessons/", lesson_list, name="lesson-list"),
    path("lessons/<int:pk>/", lesson_detail, name="lesson-detail"),
    path("lessons/<int:pk>/complete/", complete_lesson, name="lesson-complete"),

    path("enrollments/", my_enrollments, name="my-enrollments"),
]