from django.db.models import Sum, Q, Avg, Count
from django.db.models.functions import Coalesce
from rest_framework import viewsets, generics, status, permissions, parsers
from rest_framework.views import APIView
from courses.models import Category, Course, Tag, Lesson, User, Review, Enrollment, InstructorProfile, \
    TransactionStatus, Transaction, EnrollmentStatus, LessonCompleted
from courses import serializers, paginator, perms
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from courses.paginator import ReviewPagination, LessonPagination, CoursePagination
from courses.serializers import CourseSerializer, UserInfoSerializer, EnrollmentSerializer, EnrollmentDetailSerializer, \
    TransactionSerializer, StudentProgressSerializer
from rest_framework import filters
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class UserView(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]
    pagination_class = CoursePagination

    @action(methods=['get', 'patch'], url_path='current-user', detail=False,
            permission_classes=[perms.IsAuthenticated])
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            s = serializers.UserSerializer(user, data=request.data, partial=True)
            s.is_valid(raise_exception=True)
            s.save()

        return Response(serializers.UserInfoSerializer(user).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='courses', detail=True)
    def get_course_list(self, request, pk=None):
        user = self.get_object()
        courses = Course.objects.filter(instructor=user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='enrolled-courses',
            permission_classes=[permissions.IsAuthenticated])
    def enrolled_courses(self, request):
        user = request.user

        courses = Course.objects.filter(
            enrollment__user=user,
        ).distinct()
        paginator = LessonPagination()

        page = paginator.paginate_queryset(courses, request, view=self)

        if page is not None:
            serializer = serializers.CourseSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializers.CourseSerializer(courses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='transactions', permission_classes=[permissions.IsAuthenticated])
    def get_transactions(self, request, pk=None):
        user = self.get_object()
        transactions = Transaction.objects.filter(user=user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InstructorView(viewsets.ViewSet, generics.CreateAPIView):
    queryset = InstructorProfile.objects.all()
    serializer_class = serializers.IntructorProfileSerializer
    parser_classes = [parsers.MultiPartParser]


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
    queryset = Course.objects.annotate(
        total_duration=Coalesce(Sum('lessons__duration'), 0),
        avg_rating=Coalesce(Avg('review__rating'), 0.0)
    )
    pagination_class = paginator.CoursePagination
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['title', 'price', 'created_date']
    ordering = ['-created_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CourseSerializer
        return serializers.CourseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    def get_permissions(self):
        if self.action.__eq__('get_reviews') and self.request.method.__eq__('POST'):
            return [IsAuthenticated()]

        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        if self.action == 'create':
            return [permissions.IsAuthenticated(), perms.IsTeacher()]

        if self.action in ['update', 'partial_update', 'destroy', 'hide_course', 'unhide_course','students']:
            return [permissions.IsAuthenticated(), perms.IsCourseOwner()]

        if self.action == 'get_lessons':
            return [permissions.IsAuthenticated(), perms.IsEnrolled()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        query = self.queryset
        user = self.request.user

        if getattr(user, 'role', '')!= 'teacher':
            query = query.filter(active=True)
        q = self.request.query_params.get('q')
        if q:
            query = query.filter(title__icontains=q)

        category_id = self.request.query_params.get('category_id')
        if category_id:
            query = query.filter(category_id=category_id)

        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            # SỬA LẠI THÀNH: instructor_id
            query = query.filter(instructor_id=teacher_id)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            query = query.filter(price__gte=min_price)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            query = query.filter(price__lte=max_price)

        return query

    @action(methods=['get', 'post'], detail=True, url_path='reviews')
    def get_reviews(self, request, pk):
        course = self.get_object()
        if request.method == 'POST':
            is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
            if not is_enrolled:
                return Response(
                    {"error": "Bạn chưa đăng ký khóa học này nên không thể đánh giá."},
                    status=status.HTTP_403_FORBIDDEN
                )
            s = serializers.ReviewSerializer(data=request.data)

            s.is_valid(raise_exception=True)
            s.save(user=request.user, course=self.get_object())

            return Response(s.data, status=status.HTTP_201_CREATED)

        reviews = course.review_set.select_related('user').all()
        paginator = ReviewPagination()

        page = paginator.paginate_queryset(reviews, request, view=self)

        if page is not None:
            serializer = serializers.ReviewSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


        return Response(serializers.ReviewSerializer(reviews, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get', 'post'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk=None):
        course = self.get_object()
        if request.method == 'POST':
            s = serializers.LessonDetailSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            s.save(user=request.user, course=course)
            return Response(s.data, status=status.HTTP_201_CREATED)

        user = self.request.user
        if user.is_authenticated and getattr(user, 'role', '') == 'teacher':
            lessons = course.lessons.all()
        else:
            lessons = course.lessons.filter(active=True)

        paginator = LessonPagination()

        page = paginator.paginate_queryset(lessons, request, view=self)

        if page is not None:
            serializer = serializers.LessonSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK)

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

    @action(methods=['get'], detail=True, url_path='students')
    def students(self, request, pk=None):
        course = self.get_object()

        total_lessons = course.lessons.filter(active=True).count()

        users = User.objects.filter(
            enrollment__course=course
        ).distinct().annotate(
            completed_count=Count(
                'lessoncompleted',
                filter=Q(
                    lessoncompleted__lesson__course=course,
                    lessoncompleted__lesson__active=True
                )
            )
        )

        serializer = serializers.StudentProgressSerializer(
            users,
            many=True,
            context={'total_lessons': total_lessons}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonView(viewsets.ViewSet, generics.RetrieveAPIView, generics.DestroyAPIView, generics.UpdateAPIView):
    serializer_class = serializers.LessonSerializer
    pagination_class = LessonPagination

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated and getattr(user, 'role', '') == 'teacher':
            return Lesson.objects.all()
        return Lesson.objects.filter(active=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.LessonDetailSerializer
        return serializers.LessonSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated(), perms.IsEnrolled()]

        if self.action in ['update', 'partial_update', 'destroy', 'hide_lesson', 'unhide_lesson']:
            return [perms.IsCourseOwner()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='hide', url_name='hide')
    def hide_lesson(self, request, pk):
        lesson = self.get_object()
        lesson.active = False
        lesson.save()

        return Response(data=serializers.LessonSerializer(lesson).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='unhide', url_name='unhide')
    def unhide_lesson(self, request, pk):
        lesson = self.get_object()
        lesson.active = True
        lesson.save()

        return Response(data=serializers.LessonSerializer(lesson).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='complete')
    def complete_lesson(self, request, pk=None):
        lesson = self.get_object()
        user = request.user
        course = lesson.course

        lesson_completed, created = LessonCompleted.objects.get_or_create(user=user, lesson=lesson)

        total_lessons = course.lessons.filter(active=True).count()

        completed_count = LessonCompleted.objects.filter(
            user=user,
            lesson__course=course,
            lesson__active=True
        ).count()

        percent = 0
        if total_lessons > 0:
            percent = (completed_count / total_lessons) * 100

        try:
            enrollment = Enrollment.objects.get(user=user, course=course)
            enrollment.process_percent = percent

            if percent >= 100:
                enrollment.status = EnrollmentStatus.COMPLETED
            elif percent > 0 and enrollment.status == EnrollmentStatus.NOT_STARTED:
                enrollment.status = EnrollmentStatus.ENROLLED

            enrollment.save()
        except Enrollment.DoesNotExist:
            pass

        return Response({
            'message': 'Đã hoàn thành bài học',
            'process_percent': round(percent, 2),
            'completed': True
        }, status=status.HTTP_200_OK)


class ReviewView(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [perms.ReviewOwner]
    pagination_class = ReviewPagination


class EnrollmentView(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.DestroyAPIView):
    queryset = Enrollment.objects.select_related('user', 'course').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollmentSerializer
        return EnrollmentDetailSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return []


class TransactionView(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TeacherDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'teacher':
            return Response({"detail": "Bạn không có quyền truy cập."}, status=status.HTTP_403_FORBIDDEN)

        my_courses = Course.objects.filter(instructor=user)

        total_courses = my_courses.count()

        total_students = Enrollment.objects.filter(
            course__in=my_courses
        ).values('user').distinct().count()

        revenue_data = Transaction.objects.filter(
            course__in=my_courses,
            status=TransactionStatus.SUCCESS
        ).aggregate(total=Sum('amount'))

        total_revenue = revenue_data['total'] or 0

        chart_data_qs = my_courses.annotate(
            course_revenue=Sum(
                'transaction__amount',
                filter=Q(transaction__status=TransactionStatus.SUCCESS)
            )
        ).values('title', 'course_revenue').order_by('-course_revenue')
        formatted_chart_data = []
        for item in chart_data_qs:
            if item['course_revenue'] and item['course_revenue'] > 0:
                formatted_chart_data.append({
                    "name": item['title'],
                    "value": float(item['course_revenue']),
                })

        return Response({
            "summary": {
                "total_courses": total_courses,
                "total_students": total_students,
                "total_revenue": total_revenue,
            },
            "chart_data": formatted_chart_data
        }, status=status.HTTP_200_OK)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/accounts/google/login/callback/"
    client_class = OAuth2Client