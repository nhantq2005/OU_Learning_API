from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


class RoleChoice(models.TextChoices):
    TEACHER = 'teacher', 'Giảng viên'
    STUDENT = 'student', 'Sinh viên'


class GenderChoice(models.TextChoices):
    MALE = 'male', 'Nam'
    STUDENT = 'female', 'Nữ'


class User(AbstractUser):
    gender = models.CharField(choices=GenderChoice.choices, max_length=10, null=True)
    role = models.CharField(max_length=10, choices=RoleChoice.choices)
    is_verified = models.BooleanField(default=True)
    avatar = CloudinaryField(null=True)


class StatusChoice(models.TextChoices):
    PENDING = 'pending', 'Đang xử lý'
    APPROVED = 'approved', 'Chấp nhận'
    REJECTED = 'rejected', 'Từ chối'


class InstructorProfile(models.Model):
    document = CloudinaryField(null=False)
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    bank_account = models.CharField(max_length=50, null=True)
    expertise = models.CharField(max_length=255)
    # MỐI QUAN HỆ
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    image = CloudinaryField(null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    intro_video = CloudinaryField(resource_type="video", null=False)
    active = models.BooleanField(default=True)
    image = CloudinaryField(null=False)
    # MỐI QUAN HỆ
    instructor = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        unique_together = ('title', 'category')
        ordering = ['-id']


    def __str__(self):
        return self.title


class EnrollmentStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Chưa học"
    ENROLLED = "enrolled", "Đang học"
    COMPLETED = "completed", "Hoàn thành"


class Enrollment(models.Model):
    enrolled_date = models.DateTimeField(auto_now_add=True)
    process_percent = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.NOT_STARTED)
    # MỐI QUAN HỆ
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)


class Chapter(models.Model):
    title = models.CharField(max_length=255)
    # MỐI QUAN HỆ
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')

    class Meta:
        unique_together = ('title', 'course')
        ordering = ['title']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    thumbnail = CloudinaryField(null=False)
    video = CloudinaryField(resource_type="video", null=False)
    active = models.BooleanField(default=True)
    # MỐI QUAN HỆ
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')

    class Meta:
        unique_together = ('name', 'chapter')
        ordering = ['name']

    def __str__(self):
        return self.name


class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Review(Interaction):
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    class Meta:
        unique_together = ('course', 'user')

    def __str__(self):
        return self.comment


class Like(Interaction):
    class Meta:
        unique_together = ('course', 'user')

# MỞ RỘNG


# class Transaction(models.Model):
#     pass
