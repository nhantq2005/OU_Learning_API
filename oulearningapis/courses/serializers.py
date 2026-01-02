from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from courses.models import Category, Course, Tag, Enrollment, Lesson, Chapter, Review, User
from rest_framework.exceptions import ValidationError


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name','gender', 'avatar', 'role', 'is_verified']


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name','gender', 'username', 'password', 'avatar', 'role', 'is_verified']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }



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
        fields = ['id', 'name', 'thumbnail']


# LẤY CHI TIẾT BÀI HỌC
class LessonDetailSerializer(LessonSerializer):
    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['video', 'description'] #COURSE


class CourseSerializer(ImageSerializer):
    tags = TagSerializer(many=True, read_only=True)
    instructor = UserInfoSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',  # Map vào field 'category' trong Model
        write_only=True  # Chỉ dùng khi gửi lên, không hiện khi trả về
    )

    tags_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',  # Kết nối với field 'tags' trong Model Lesson
        many=True,  # Quan trọng: Cho phép gửi nhiều ID
        write_only=True
    )

    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='instructor',  # Kết nối với field 'tags' trong Model Lesson  # Quan trọng: Cho phép gửi nhiều ID
        write_only=True
    )

    class Meta:
        model = Course
        fields = ['id', 'title',  'price', 'image', 'category', 'tags', 'instructor', 'category_id', 'tags_id', 'instructor_id']


    #
    # def create(self, validated_data):
    #     # 1. Tách dữ liệu nested ra khỏi validated_data
    #     tags_data = validated_data.pop('tags')
    #     category_data = validated_data.pop('category')
    #
    #     # 2. Xử lý Category: Lấy cái đã có hoặc tạo mới
    #     category_obj, _ = Category.objects.get_or_create(**category_data)
    #
    #     # 3. Tạo Course trước
    #     course = Course.objects.create(category=category_obj, **validated_data)
    #
    #     # 4. Xử lý Tags: Lấy cái đã có hoặc tạo mới rồi add vào course
    #     for tag_data in tags_data:
    #         tag_obj, _ = Tag.objects.get_or_create(**tag_data)
    #         course.tags.add(tag_obj)
    #
    #     return course

class CourseDetailSerializer(CourseSerializer):


    class Meta:
        model = CourseSerializer.Meta.model
        fields = CourseSerializer.Meta.fields + [ 'intro_video','description']


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title','course']


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


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

    validators = [
        UniqueTogetherValidator(
            queryset=Enrollment.objects.all(),
            fields=['user', 'course'],
            message="Bạn đã đăng ký khóa học này rồi."
        )
    ]
