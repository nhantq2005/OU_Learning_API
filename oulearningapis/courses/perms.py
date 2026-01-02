from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, BasePermission

from courses.models import Lesson, Chapter, Course, Enrollment


class ReviewOwner(IsAuthenticated):
    def has_object_permission(self, request, view, review):
        return super().has_permission(request, view) and request.user == review.user


class HasLearnedCourse(BasePermission):
    message = "Bạn phải tham gia khóa học này trước khi được phép review."

    def has_permission(self, request, view):
        # Chỉ áp dụng khi tạo review
        if request.method != "POST":
            return True

        course_id = request.data.get("course_id")
        if not course_id:
            return False

        user = request.user

        # Kiểm tra người dùng đã đăng ký học chưa
        from .models import Enrollment
        return Enrollment.objects.filter(user=user, course_id=course_id).exists()


class IsEnrolled(permissions.BasePermission):
    message = "Bạn chưa đăng ký khóa học này."

    def has_object_permission(self, request, view, obj):
        # 1. Phải đăng nhập mới được kiểm tra tiếp
        if not request.user.is_authenticated:
            return False

        # 2. Xác định Course từ object hiện tại (Bài học -> Chương -> Khóa học)
        course = None
        if isinstance(obj, Lesson):
            course = obj.chapter.course
        elif isinstance(obj, Chapter):
            course = obj.course
        elif isinstance(obj, Course):
            course = obj

        # 3. Nếu user là Giảng viên (chủ khóa học) hoặc Superuser thì luôn cho phép
        if course and (request.user == course.instructor or request.user.is_superuser):
            return True

        # 4. Kiểm tra trong bảng Enrollment xem user đã đăng ký course này chưa
        return Enrollment.objects.filter(user=request.user, course=course).exists()

    # perms.py (Code này đã có trong file của bạn, chỉ cần đảm bảo giữ nguyên logic này)

    class IsEnrolled(permissions.BasePermission):
        message = "Bạn chưa đăng ký khóa học này."

        def has_object_permission(self, request, view, obj):
            # ... (check login)

            # Logic tìm khóa học từ bài học
            course = None
            if isinstance(obj, Lesson):
                course = obj.chapter.course  # <--- Quan trọng: Từ Lesson tìm ra Course
            # ... (các trường hợp khác)

            # ... (check giảng viên/admin)

            # Kiểm tra bảng Enrollment
            return Enrollment.objects.filter(user=request.user, course=course).exists()


class IsCourseOwner(permissions.BasePermission):
    """
    Quyền sở hữu:
    - Admin: Toàn quyền.
    - Giảng viên: Chỉ được thao tác trên khóa học/bài học do chính mình tạo.
    """

    def has_object_permission(self, request, view, obj):
        # 1. Admin luôn có quyền
        if request.user.is_superuser:
            return True

        # 2. Logic kiểm tra chủ sở hữu (Instructor)
        # Nếu obj là Course -> check instructor
        if isinstance(obj, Course):
            return obj.instructor == request.user

        # Nếu obj là Chapter -> check course.instructor
        if isinstance(obj, Chapter):
            return obj.course.instructor == request.user

        # Nếu obj là Lesson -> check chapter.course.instructor
        if isinstance(obj, Lesson):
            return obj.chapter.course.instructor == request.user

        return False