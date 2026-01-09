from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from courses.models import Category, Course, Tag, Enrollment, Lesson, Review, User, InstructorProfile
from rest_framework.exceptions import ValidationError


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'gender', 'avatar', 'role', 'is_active', 'email']


class UserSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'gender', 'username', 'password', 'avatar', 'role', 'is_active',
                  'email']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class IntructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = ['id', 'document', 'bank_account', 'expertise', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.document:
            data['document'] = instance.document.url

        return data


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
        fields = ['id', 'name', 'thumbnail', 'active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.thumbnail:
            data['thumbnail'] = instance.thumbnail.url

        return data


# LẤY CHI TIẾT BÀI HỌC
class LessonDetailSerializer(LessonSerializer):
    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['video', 'description']  # COURSE

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.video:
            data['video'] = instance.video.url

        return data

    def create(self, validated_data):
        # Loại bỏ trường 'user' nếu nó tồn tại trong validated_data
        # để tránh lỗi TypeError khi gọi Lesson.objects.create()
        # XEM KỸ
        validated_data.pop('user', None)

        return super().create(validated_data)


class CourseSerializer(ImageSerializer):
    avg_rating = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        result = obj.review_set.aggregate(Avg('rating'))
        rating = result['rating__avg']

        # Nếu có rating thì làm tròn, nếu None thì trả về 0
        if rating:
            return round(rating, 1)
        return 0

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

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     if instance.image:
    #         data['image'] = instance.image.url
    #
    #     return data

    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'image', 'category', 'tags', 'instructor', 'category_id', 'tags_id',
                  'instructor_id', 'avg_rating', 'active']

    #
    # def create(self, validated_data):
    #     # 1. Tách dữ liệu nested ra khỏi validated_data
    #     tags_data = validated_data.pop('tags')
    #
    #     # 4. Xử lý Tags: Lấy cái đã có hoặc tạo mới rồi add vào course
    #     for tag_data in tags_data:
    #         tag_obj, _ = Tag.objects.get_or_create(**tag_data)
    #         course.tags.add(tag_obj)
    #
    #     return course


class CourseDetailSerializer(CourseSerializer):
    # 1. Khai báo thêm trường is_enrolled
    is_enrolled = serializers.SerializerMethodField()

    def get_is_enrolled(self, obj):
        request = self.context.get('request')

        # 1. Kiểm tra request và user hợp lệ
        if not request or not request.user.is_authenticated:
            return False

        # 2. Truy vấn trực tiếp từ bảng Enrollment (Sạch và nhanh hơn)
        return Enrollment.objects.filter(
            user=request.user,
            course=obj
        ).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.intro_video:
            data['intro_video'] = instance.intro_video.url

        return data

    class Meta:
        model = CourseSerializer.Meta.model
        fields = CourseSerializer.Meta.fields + ['intro_video', 'description', 'is_enrolled']


class ReviewSerializer(serializers.ModelSerializer):
    # Serializer để hiển thị thông tin user đầy đủ (Avatar, Tên) thay vì chỉ hiện ID
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_date', 'user', 'course']
        # Đặt course là read_only vì ta lấy từ URL, không lấy từ body JSON
        read_only_fields = ['user', 'course', 'created_date']


class ReviewDetailSerializer(ReviewSerializer):
    user = UserInfoSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = ReviewSerializer.Meta.model
        fields = ReviewSerializer.Meta.fields + ['created_date', 'user', 'course']


class EnrollmentSerializer(serializers.ModelSerializer):
    # 1. Tự động lấy user đang login, ẩn khỏi form nhập liệu
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())


    class Meta:
        model = Enrollment
        fields = ['course', 'user']

    validators = [
        UniqueTogetherValidator(
            queryset=Enrollment.objects.all(),
            fields=['user', 'course'],
            message="Bạn đã đăng ký khóa học này rồi."
        )
    ]

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     return Enrollment.objects.create(user=user, **validated_data)


class EnrollmentDetailSerializer(EnrollmentSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = EnrollmentSerializer.Meta.fields + ['enrolled_date', 'process_percent', 'status', 'course']
