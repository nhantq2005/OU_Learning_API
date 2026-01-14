from django.db.models import Avg, Sum
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from courses.models import Category, Course, Tag, Enrollment, Lesson, Review, User, InstructorProfile, Transaction, \
    LessonCompleted
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


class LessonDetailSerializer(LessonSerializer):
    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['video', 'description', 'duration']  # COURSE

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.video:
            data['video'] = instance.video.url

        return data

    def create(self, validated_data):
        # XEM KỸ
        validated_data.pop('user', None)

        return super().create(validated_data)


class CourseSerializer(ImageSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    total_duration = serializers.IntegerField(read_only=True)

    tags = TagSerializer(many=True, read_only=True)
    instructor = UserInfoSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    tags_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True
    )

    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='instructor',
        write_only=True
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'image', 'category', 'tags', 'instructor', 'category_id', 'tags_id',
                  'instructor_id', 'avg_rating', 'active','total_duration']


class CourseDetailSerializer(CourseSerializer):
    is_enrolled = serializers.SerializerMethodField()

    def get_is_enrolled(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False

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
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_date', 'user', 'course']
        read_only_fields = ['user', 'course', 'created_date']


class ReviewDetailSerializer(ReviewSerializer):
    user = UserInfoSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = ReviewSerializer.Meta.model
        fields = ReviewSerializer.Meta.fields + ['created_date', 'user', 'course']


class EnrollmentSerializer(serializers.ModelSerializer):
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


class EnrollmentDetailSerializer(EnrollmentSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = EnrollmentSerializer.Meta.fields + ['enrolled_date', 'process_percent', 'status', 'course']


class TransactionSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_info = UserInfoSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = ['created_date','user_info','amount', 'status', 'course']



class StudentProgressSerializer(serializers.ModelSerializer):
    process_percent = serializers.SerializerMethodField()
    completed_count = serializers.IntegerField(read_only=True)

    def get_process_percent(self, user):
        total_lessons = self.context.get('total_lessons', 0)

        if total_lessons == 0:
            return 0.0

        completed = getattr(user, 'completed_count', 0)

        return round((completed / total_lessons) * 100, 2)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'avatar', 'email',
                  'process_percent', 'completed_count']


class LessonCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompleted
        fields = '__all__'