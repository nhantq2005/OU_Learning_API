from rest_framework import serializers
from courses.models import Category, Course, Tag, Enrollment, Lesson, Chapter, Review, User
from rest_framework.exceptions import ValidationError


class ImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url

        return data


class CategorySerializer(ImageSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


# LẤY CHI TIẾT BÀI HỌC
class LessonDetailSerializer(LessonSerializer):
    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'price', 'intro_video', 'duration_minutes']


# LẤY CHI TIẾT KHÓA HỌC
class CourseDetailSerializer(CourseSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = CourseSerializer.Meta.model
        fields = CourseSerializer.Meta.fields


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'created_date', 'user', 'course']
        extra_kwargs = {
            'lesson': {
                'write_only': True
            }
        }

        def to_representation(self, instance):
            data = super().to_representation(instance)
            if instance.avatar:
                data['avatar'] = instance.avatar.url

            return data

        def create(self, validated_data):
            user = User(**validated_data)
            user.set_password(user.password)
            user.save()

            return user

        def update(self, instance, validated_data):
            keys = set(validated_data.keys())
            if keys - {'first_name', 'last_name', 'email'}:
                raise ValidationError({'error': 'Invalid fields'})

            return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }



class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'