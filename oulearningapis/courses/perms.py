from rest_framework import permissions, request
from rest_framework.permissions import IsAuthenticated, BasePermission

from courses.models import Lesson, Course, Enrollment, RoleChoice


class ReviewOwner(IsAuthenticated):
    def has_object_permission(self, request, view, review):
        return super().has_permission(request, view) and request.user == review.user


class HasLearnedCourse(BasePermission):
    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        course_id = request.data.get("course_id")
        if not course_id:
            return False
        user = request.user
        return Enrollment.objects.filter(user=user, course_id=course_id).exists()


class IsEnrolled(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        course = None
        if isinstance(obj, Lesson):
            course = obj.course
        elif isinstance(obj, Course):
            course = obj

        if course and (request.user == course.instructor or request.user.is_superuser):
            return True

        return Enrollment.objects.filter(user=request.user, course=course).exists()


class IsCourseOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if isinstance(obj, Course):
            return obj.instructor == request.user

        if isinstance(obj, Lesson):
            return obj.course.instructor == request.user

        return False

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == RoleChoice.TEACHER and request.user.is_authenticated