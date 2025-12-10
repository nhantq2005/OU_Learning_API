from rest_framework.permissions import IsAuthenticated, BasePermission


class ReviewOwner(IsAuthenticated):
    def has_object_permission(self, request, view, review):
        return super().has_permission(request, view) and request.user == review.user


# class HasLearnedCourse(BasePermission):
#     message = "Bạn phải tham gia khóa học này trước khi được phép review."
#
#     def has_permission(self, request, view):
#         # Chỉ áp dụng khi tạo review
#         if request.method != "POST":
#             return True
#
#         course_id = request.data.get("course_id")
#         if not course_id:
#             return False
#
#         user = request.user
#
#         # Kiểm tra người dùng đã đăng ký học chưa
#         from .models import Enrollment
#         return Enrollment.objects.filter(user=user, course_id=course_id).exists()
