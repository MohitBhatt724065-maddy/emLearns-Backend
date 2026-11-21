
from django.contrib import admin
from .models import Course, Module, Lesson


# Modules inside Course
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ("title", "description", "order")
    ordering = ("order",)


# Lessons inside Module
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    fields = (
        "title",
        "description",
        "content",
        "order",
        "video_url",
        "is_published",
        "image",
    )
    ordering = ("order",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title", "description")
    ordering = ("title",)

    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order")
    search_fields = ("title", "description", "course__title")
    list_filter = ("course",)
    ordering = ("course", "order")
    list_select_related = ("course",)

    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "module",
        "is_published",
        "order",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "content",
        "module__title",
        "module__course__title",
    )
    list_filter = ("is_published", "created_at")
    ordering = ("module", "order")
    list_select_related = ("module", "module__course")
