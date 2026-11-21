from django.urls import path

from .views import (
    course_list,
    module_list,
    lesson_list,
    course_detail,
    module_detail,
    lesson_detail,
)


urlpatterns = [
    path("courses/", course_list, name="course-list"),
    path("modules/", module_list, name="module-list"),
    path("lessons/", lesson_list, name="lesson-list"),
    
    path("courses/<int:pk>/", course_detail, name="course-detail"),
    path("modules/<int:pk>/", module_detail, name="module-detail"),
    path("lessons/<int:pk>/", lesson_detail, name="lesson-detail"),
]
