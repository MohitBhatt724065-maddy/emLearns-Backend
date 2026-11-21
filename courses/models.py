from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    video_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
    upload_to="lessons/",
    blank=True,
    null=True
   )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title