from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions, parsers
from courses.models import Category, Course, Chapter, Tag, Lesson, User, Review, Enrollment
from courses import serializers, paginator, perms
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from courses.serializers import CourseSerializer


class UserView(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False,
            permission_classes=[perms.IsAuthenticated])
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            s = serializers.UserSerializer(user, data=request.data, partial=True)
            s.is_valid(raise_exception=True)
            s.save()

        return Response(serializers.UserInfoSerializer(user).data, status=status.HTTP_200_OK)

    # ACTIVE ACCOUNT CHO GV
    @action(methods=['post'], detail=True)
    def active_user(self, request, pk):
        user = self.get_object()
        user.is_verified = True
        user.save()

        return Response(serializers.UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='courses', detail=True)
    def get_course_list(self, request, pk=None):
        user = self.get_object()
        courses = Course.objects.filter(íntructor=user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='enrolled-courses')
    def enrolled_courses(self, request):
        user = request.user

        courses = Course.objects.filter(
            enrollments__user=user,
            active=True
        ).distinct()

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryView(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer
    pagination_class = paginator.CategoryPagination

    @action(methods=['post'], detail=True, url_path='hide')
    def hide_category(self, request, pk=None):
        category = self.get_object()
        category.active = False
        category.save()
        return Response(data=serializers.CategorySerializer(category).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='unhide')
    def unhide_category(self, request, pk=None):
        category = self.get_object()
        category.active = True
        category.save()
        return Response(data=serializers.CategorySerializer(category).data, status=status.HTTP_200_OK)


class TagView(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Tag.objects.filter(active=True)
    serializer_class = serializers.TagSerializer


class CourseView(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView,
                 generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Course.objects.filter(active=True)
    # serializer_class = serializers.CourseDetailSerializer
    pagination_class = paginator.CoursePagination

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CourseSerializer
        return serializers.CourseDetailSerializer

    # KIỂM TRA QUYỀN
    # def get_permissions(self):
    #     if self.action.__eq__('get_reviews') and self.request.method.__eq__('POST'):
    #         return [IsAuthenticated()]

        return [AllowAny()]

    # def get_permissions(self):
    #     # 1. Xem danh sách/chi tiết: Ai cũng xem được
    #     if self.action in ['list', 'retrieve']:
    #         return [permissions.AllowAny()]
    #
    #     # 2. Thêm mới (Create): Phải đăng nhập
    #     if self.action == 'create':
    #         return [permissions.IsAuthenticated()]
    #
    #     # 3. Sửa, Xóa, Ẩn: Chỉ chủ sở hữu hoặc Admin
    #     if self.action in ['update', 'partial_update', 'destroy', 'hide_course', 'unhide_course', 'get_chapters']:
    #         return [perms.IsCourseOwner()]
    #
    #     return [permissions.AllowAny()]
    #
    # # QUAN TRỌNG: Gán người tạo là instructor
    # def perform_create(self, serializer):
    #     serializer.save(instructor=self.request.user)

    def get_queryset(self):
        query = self.queryset

        # TÌM KIẾM BẰNG TỪ KHÓA
        q = self.request.query_params.get('q')
        if q:
            query = query.filter(title__icontains=q)

        # LỌC THEO CATEGORY
        category_id = self.request.query_params.get('category_id')
        if category_id:
            query = query.filter(category_id=category_id)

        return query

    # LẤY CÁC CHƯƠNG CỦA KHÓA
    @action(methods=['post'], detail=True, url_path='chapters')
    def get_chapters(self, request, pk):
        course = self.get_object()
        chapter = serializers.ChapterSerializer(data={
            'title': request.data.get('title'),
            'course': self.get_object().pk,
        })
        chapter.is_valid(raise_exception=True)
        c = chapter.save()
        return Response(serializers.ChapterSerializer(c).data, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     # Ví dụ: Gán người tạo bài học là user hiện tại
    #     serializer.save(author=self.request.user)


# @action(methods=['get', 'post'], detail=True, url_path='chapters')
# def chapters(self, request, pk=None):
#     course = self.get_object()
#
#     if request.method == 'POST':
#         data = request.data.copy()
#         data['course'] = course.id
#
#         serializer = serializers.ChapterSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(
#             serializer.data,
#             status=status.HTTP_201_CREATED
#         )
#
#     # GET chapters
#     chapters = course.chapters.filter(active=True)
#     serializer = serializers.ChapterSerializer(chapters, many=True)
#
#     return Response(serializer.data, status=status.HTTP_200_OK)

# TẠO VÀ LẤY TAG CỦA KHÓA HỌC
# @action(methods=['get', 'post'], detail=True, url_path='tags')
# def get_tags(self, request, pk):
#     if request.method.__eq__('POST'):
#         pass
#
#     tags = self.get_object().tag_set.filter(active=True)
#     return Response(serializers.TagSerializer(tags, many=True).data, status.HTTP_200_OK)

    # TẠO VÀ LẤY ĐÁNH GIÁ KHÓA HỌC
    @action(methods=['get', 'post'], detail=True, url_path='reviews')
    def get_reviews(self, request, pk):
        if request.method.__eq__('POST'):
            s = serializers.ReviewSerializer(data={
                'comment': request.data.get('comment'),
                'rating': request.data.get('rating'),
                'user': self.request.user.pk,
                'course': self.get_object().pk,
            })
            s.is_valid(raise_exception=True)
            c = s.save()
            return Response(serializers.ReviewSerializer(c).data, status=status.HTTP_201_CREATED)

        # GET ĐÁNH GIÁ
        reviews = self.get_object().review_set.select_related('user').filter(active=True)
        return Response(serializers.ReviewSerializer(reviews, many=True).data, status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='hide')
    def hide_course(self, request, pk=None):
        course = self.get_object()
        course.active = False
        course.save()
        return Response(data=serializers.CourseDetailSerializer(course).data, status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='unhide')
    def unhide_course(self, request, pk=None):
        course = self.get_object()
        course.active = True
        course.save()
        return Response(data=serializers.CourseDetailSerializer(course).data, status=status.HTTP_200_OK)

# @action(methods=['post'], detail=True, url_path='add-tag')
# def add_tag(self, request, pk):
#     course = self.get_object()
#     tag_id = request.data.get("tag_id")
#
#     if not Tag.objects.filter(id=tag_id).exists():
#         return Response(data=serializers.TagSerializer(tag_id).data, status=status.HTTP_400_BAD_REQUEST)
#
#     course.tag_set.add(tag_id)
#     return Response(data=serializers.TagSerializer(tag_id).data, status=status.HTTP_200_OK)

# @action(methods=['post'], detail=True, url_path='remove-tag')
# def remove_tag(self, request, pk):
#     course = self.get_object()
#     tag_id = request.data.get("tag_id")
#
#     course.tag_set.remove(tag_id)
#     return Response(data=serializers.TagSerializer(tag_id).data, status=status.HTTP_200_OK)


class ChapterView(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer

    @action(methods=['get'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk):
        lessons = self.get_object().lesson.filter(active=True)

        return Response(serializers.LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='hide')
    def hide_chapter(self, request, pk):
        chapter = self.get_object()
        chapter.active = False
        chapter.save()

        return Response(data=serializers.ChapterSerializer(chapter).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='unhide')
    def unhide_chapter(self, request, pk):
        chapter = self.get_object()
        chapter.active = True
        chapter.save()

        return Response(data=serializers.ChapterSerializer(chapter).data, status=status.HTTP_200_OK)


class LessonView(viewsets.ViewSet, generics.RetrieveAPIView, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = serializers.LessonSerializer

    # def get_permissions(self):
    #     # 1. Nếu xem chi tiết bài học (Xem video): Phải đăng nhập VÀ Đã đăng ký
    #     if self.action == 'retrieve':
    #         return [permissions.IsAuthenticated(), perms.IsEnrolled()]
    #
    #     # 2. Nếu sửa/xóa/ẩn bài học: Chỉ giảng viên (chủ khóa học) hoặc Admin
    #     if self.action in ['update', 'partial_update', 'destroy', 'hide_lesson', 'unhide_lesson']:
    #         return [perms.IsCourseOwner()]  # Sử dụng class IsCourseOwner bạn đã tạo ở bước trước
    #
    #     return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='hide', url_name='hide')
    def hide_lesson(self, request, pk):
        lesson = self.get_object()
        lesson.active = False
        lesson.save()

        return Response(data=serializers.LessonSerializer(lesson).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='unhide', url_name='unhide')
    def unhide_chapter(self, request, pk):
        lesson = self.get_object()
        lesson.active = True
        lesson.save()

        return Response(data=serializers.LessonSerializer(lesson).data, status=status.HTTP_200_OK)


class ReviewView(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [perms.ReviewOwner]


class EnrollmentView(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = serializers.EnrollmentSerializer

