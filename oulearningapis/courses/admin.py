import json

from django.contrib import admin
from django.utils.safestring import mark_safe
from courses.models import Category, Course, Lesson, Tag, Review, Enrollment, User, Transaction, TransactionStatus, \
    InstructorProfile
from django.core.mail import send_mail
from django.conf import settings

admin.site.site_header = "Hệ thống Quản lý OU Learning"
admin.site.site_title = "OU Learning Admin"
admin.site.index_title = "Danh sách quản trị"


class InstructorProfileInline(admin.StackedInline):
    model = InstructorProfile
    can_delete = False
    verbose_name_plural = 'Hồ sơ giảng viên'
    fk_name = 'user'

    readonly_fields = ['view_document']

    def view_document(self, obj):
        if obj.document:
            return mark_safe(
                f'<img src="{obj.document.url}" width="300" style="border-radius: 5px; border: 1px solid #ccc;" />')
        return "Chưa cập nhật tài liệu"

    view_document.short_description = "Ảnh minh chứng"

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']
    inlines = [InstructorProfileInline]

    readonly_fields = ['avatar_display']

    actions = ['activate_users_and_notify', 'deactivate_users_and_notify']

    def avatar_display(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />')
        return ""

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_user = User.objects.get(pk=obj.pk)
                if not old_user.is_active and obj.is_active:
                    self.send_activation_email(request, obj)

            except User.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

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


    @admin.action(description='Chấp nhận')
    def activate_users_and_notify(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save()
                self.send_activation_email(request, user)
                count += 1
        self.message_user(request, f"Đã kích hoạt {count} tài khoản.")

    @admin.action(description='Từ chối')
    def deactivate_users_and_notify(self, request, queryset):
        count = 0
        for user in queryset:
            if not user.is_active:
                self.send_deactivation_email(request, user)
                user.delete()
                count += 1
        self.message_user(request, f"Đã kích hoạt {count} tài khoản.")


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'enrolled_date']
    list_select_related = ['user', 'course']


admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Review)
admin.site.register(Transaction)
