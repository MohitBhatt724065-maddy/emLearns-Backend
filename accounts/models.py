from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    institution = models.CharField(
        max_length=255,
        blank=True
    )

    academic_level = models.CharField(
        max_length=100,
        blank=True
    )

    bio = models.TextField(blank=True)

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"