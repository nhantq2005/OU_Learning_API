from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions, parsers
from courses.models import Category, Course, Chapter, Tag, Lesson, User, Review, Enrollment
from courses import serializers, paginator, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class UserView(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            s = serializers.UserSerializer(user, data=request.data, partial=True)
            s.is_valid(raise_exception=True)
            s.save()

        return Response(serializers.UserSerializer(user).data, status=status.HTTP_200_OK)


class CategoryView(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    pagination_class = paginator.CategoryPagination


class TagView(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Tag.objects.filter(active=True)
    serializer_class = serializers.TagSerializer


class CourseView(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView,
                 generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = paginator.CoursePagination

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

        # LOC THEO NHIEU TAG
        # tags = self.request.query_params.getlist('tags')
        # if tags:
        #     query = query.filter(tags__id__in=tags).distinct()

        return query


    # def add_tag(self,request, pk):
    #     course = Course.objects.get(pk=pk)

    # LẤY CÁC CHƯƠNG CỦA KHÓA
    @action(methods=['get', 'post'], detail=True, url_path='chapters')
    def get_chapters(self, request, pk):
        chapters = self.get_object().chapter_set.filter(active=True)
        return Response(serializers.ChapterSerializer(chapters, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='tags')
    def get_tags(self, request, pk):
        tags = self.get_object().tag_set.filter(active=True)
        return Response(serializers.TagSerializer(tags, many=True).data, status.HTTP_200_OK)

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

        reviews = self.get_object().review_set.select_related('user').filter(active=True)
        return Response(serializers.ReviewSerializer(reviews, many=True).data, status=status.HTTP_200_OK)


class ChapterView(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer

    @action(methods=['get'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk):
        lessons = self.get_object().lesson.filter(active=True)

        return Response(serializers.LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK)


class LessonView(viewsets.ViewSet, generics.RetrieveAPIView, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = serializers.LessonSerializer


class ReviewView(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.ReviewOwner]

class EnrollmentView(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Enrollment.objects.all()
    # serializer_class = serializers.E
