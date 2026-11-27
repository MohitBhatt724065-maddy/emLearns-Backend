from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course, Enrollment, Lesson, LessonProgress, Module


class CourseTestData(APITestCase):
    """Shared setup: one published course with 2 published lessons and 1 draft
    lesson, one unpublished course, and one student."""

    def setUp(self):
        self.course = Course.objects.create(
            title="Neuroscience Foundations", description="Basics", is_published=True
        )
        self.draft_course = Course.objects.create(
            title="Draft", description="Not ready", is_published=False
        )
        module = Module.objects.create(course=self.course, title="Neurons", order=1)
        self.lesson1 = Lesson.objects.create(
            module=module, title="The neuron", order=1, is_published=True
        )
        self.lesson2 = Lesson.objects.create(
            module=module, title="The synapse", order=2, is_published=True
        )
        self.draft_lesson = Lesson.objects.create(
            module=module, title="Unfinished", order=3, is_published=False
        )
        self.student = User.objects.create_user(
            "maya", "maya@example.com", "Neuro!2026pass"
        )


class CatalogTests(CourseTestData):
    """What anyone, logged in or not, can see."""

    def test_catalog_lists_only_published_courses(self):
        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [c["title"] for c in response.data]
        self.assertEqual(titles, ["Neuroscience Foundations"])
        self.assertEqual(response.data[0]["lesson_count"], 2)

    def test_draft_course_detail_returns_404(self):
        response = self.client.get(f"/api/courses/{self.draft_course.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_detail_hides_unpublished_lessons(self):
        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson_titles = [l["title"] for l in response.data["modules"][0]["lessons"]]
        self.assertEqual(lesson_titles, ["The neuron", "The synapse"])
        self.assertFalse(response.data["is_enrolled"])


class EnrollmentAndProgressTests(CourseTestData):
    """What a logged-in student can do."""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.student)

    def test_enroll_requires_login(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"/api/courses/{self.course.id}/enroll/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enrolling_twice_does_not_duplicate(self):
        first = self.client.post(f"/api/courses/{self.course.id}/enroll/")
        second = self.client.post(f"/api/courses/{self.course.id}/enroll/")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_cannot_complete_lesson_without_enrolling(self):
        response = self.client.post(f"/api/lessons/{self.lesson1.id}/complete/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(LessonProgress.objects.exists())

    def test_completing_a_lesson_updates_progress(self):
        self.client.post(f"/api/courses/{self.course.id}/enroll/")
        self.client.post(f"/api/lessons/{self.lesson1.id}/complete/")

        response = self.client.get("/api/enrollments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        enrollment = response.data[0]
        self.assertEqual(enrollment["completed_lessons"], 1)
        self.assertEqual(enrollment["total_lessons"], 2)
        self.assertEqual(enrollment["progress_percent"], 50)
        self.assertEqual(enrollment["next_lesson_id"], self.lesson2.id)

    def test_progress_never_exceeds_100_when_lesson_unpublished(self):
        # Regression test for the bug fixed on 27 Nov
        self.client.post(f"/api/courses/{self.course.id}/enroll/")
        self.client.post(f"/api/lessons/{self.lesson1.id}/complete/")
        self.client.post(f"/api/lessons/{self.lesson2.id}/complete/")
        self.lesson2.is_published = False
        self.lesson2.save()

        response = self.client.get(f"/api/courses/{self.course.id}/progress/")

        self.assertEqual(response.data["completed_lessons"], 1)
        self.assertEqual(response.data["total_lessons"], 1)
        self.assertEqual(response.data["progress_percent"], 100)

    def test_students_only_see_their_own_enrollments(self):
        other = User.objects.create_user("ravi", "ravi@example.com", "Neuro!2026pass")
        Enrollment.objects.create(user=other, course=self.course)

        response = self.client.get("/api/enrollments/")

        self.assertEqual(response.data, [])