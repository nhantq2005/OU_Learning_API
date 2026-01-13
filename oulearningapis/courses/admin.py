import json

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from courses.models import Category, Course, Lesson, Tag, Review, Enrollment, User, Transaction, TransactionStatus
from django import forms
# from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings


# admin.py

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']

    # Khai báo các hành động (Actions)
    actions = ['activate_users_and_notify', 'deactivate_users_and_notify']

    def save_model(self, request, obj, form, change):
        if change:
            try:
                # Lấy dữ liệu cũ trong Database
                old_user = User.objects.get(pk=obj.pk)

                # CHỈ GIỮ LẠI LOGIC ACTIVE (Đã xóa logic verify gây lỗi)
                if not old_user.is_active and obj.is_active:
                    self.send_activation_email(request, obj)

            except User.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

    # Hàm gửi mail Active (Giữ nguyên code cũ của bạn)
    def send_activation_email(self, request, user):
        if not user.email:
            return
        subject = 'Thông báo kích hoạt tài khoản'
        message = (f"""Xin chào {user.first_name},
                                
Tài khoản "{user.username}" của bạn đã được kích hoạt thành công.
Hiện tại bạn có thể đăng nhập và sử dụng đầy đủ các chức năng của ứng dụng.

Trân trọng,
Ban quản trị OU Learning.
"""
)
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            self.message_user(request, f"Đã gửi mail Active tới {user.email}")
        except Exception as e:
            print(f"Lỗi gửi mail: {e}")


    # --- HÀM MỚI: Gửi mail Verify ---
    def send_deactivation_email(self, request, user):

        if not user.email:
            return
        subject = 'Thông báo kích hoạt tài khoản'
        message = (f'''Xin chào {user.first_name} {user.last_name},
Cảm ơn bạn đã gửi yêu cầu xác thực tài khoản "{user.username}".

Sau khi xem xét, Ban quản trị rất tiếc phải thông báo rằng tài khoản của bạn chưa đủ điều kiện để được xác thực tại thời điểm này.  
Lý do có thể : thông tin hồ sơ chưa đáp ứng các tiêu chí dành cho giảng viên/người dùng trên hệ thống.
 
Nếu cần hỗ trợ thêm, đừng ngần ngại liên hệ với Ban quản trị.

Trân trọng,
Ban quản trị OU Learning.''')
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            self.message_user(request, f"Đã gửi mail Active tới {user.email}")
        except Exception as e:
            print(f"Lỗi gửi mail: {e}")



    # --- Action cũ: Active hàng loạt ---
    @admin.action(description='Chấp nhận')
    def activate_users_and_notify(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.is_active:
                self.send_activation_email(request, user)
                count += 1
        self.message_user(request, f"Đã kích hoạt {count} tài khoản.")

    @admin.action(description='Từ chối')
    def deactivate_users_and_notify(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.is_active:
                self.send_deactivation_email(request, user)
                count += 1
        self.message_user(request, f"Đã kích hoạt {count} tài khoản.")


# admin.py
# TẠI SAO TỐI ƯU QUERY
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'enrolled_date']
    # Thêm dòng này để tối ưu query trong Admin
    list_select_related = ['user', 'course']



#
# @staff_member_required
# def admin_stats_view(request):
#     # --- 1. SỐ LIỆU TỔNG QUAN (SUMMARY) ---
#     total_courses = Course.objects.count()
#
#     # Đếm học viên (distinct user trong enrollment)
#     total_students = Enrollment.objects.values('user').distinct().count()
#
#     # Tổng doanh thu (Chỉ tính giao dịch thành công)
#     revenue_agg = Transaction.objects.filter(
#         status=TransactionStatus.SUCCESS
#     ).aggregate(total=Sum('amount'))
#     total_revenue = revenue_agg['total'] or 0
#
#     # --- 2. SỐ LIỆU BIỂU ĐỒ (CHART DATA) ---
#     # Lấy top 5 khóa học doanh thu cao nhất
#     top_courses = Course.objects.annotate(
#         revenue=Sum(
#             'transaction__amount',
#             filter=Q(transaction__status=TransactionStatus.SUCCESS)
#         )
#     ).exclude(revenue=None).order_by('-revenue')[:5]  # Lấy top 5
#
#     # Chuẩn bị dữ liệu để đẩy xuống ChartJS
#     # Cần convert sang list để dùng json.dumps
#     chart_labels = []
#     chart_values = []
#
#     for course in top_courses:
#         chart_labels.append(course.title)
#         chart_values.append(float(course.revenue))  # Convert Decimal sang float
#
#     # --- 3. GIAO DỊCH GẦN ĐÂY (TABLE) ---
#     recent_transactions = Transaction.objects.select_related('user', 'course').order_by('-created_date')[:5]
#
#     context = {
#         # Số liệu hiển thị trực tiếp
#         "total_courses": total_courses,
#         "total_students": total_students,
#         "total_revenue": total_revenue,
#         "recent_transactions": recent_transactions,
#
#         # Dữ liệu Chart (Chuyển sang JSON string để JS đọc được)
#         "chart_labels_json": json.dumps(chart_labels),
#         "chart_data_json": json.dumps(chart_values),
#
#         **admin.site.each_context(request),
#         "title": "Thống kê hệ thống"
#     }
#
#     return render(request, 'templates/stats.html', context)
#
#
#
# @admin.register(StatsDashboard)
# class StatsDashboardAdmin(admin.ModelAdmin):
#     # Ghi đè hàm changelist_view để khi bấm vào menu nó chạy view thống kê
#     def changelist_view(self, request, extra_context=None):
#         return admin_stats_view(request)
#
#     # Ẩn các nút thêm/sửa/xóa
#     def has_add_permission(self, request): return False
#     def has_change_permission(self, request, obj=None): return False
#     def has_delete_permission(self, request, obj=None): return False

admin.site.register(Enrollment, EnrollmentAdmin)

admin.site.register(User, UserAdmin)

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Review)
admin.site.register(Transaction)
