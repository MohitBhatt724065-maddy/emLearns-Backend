from django.urls import path
from .views import  course_list

urlpatterns = [
    # path("", api_home, name="api-home"),
    path("courses/", course_list, name="course-list"),
]