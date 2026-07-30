from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


class RoleChoice(models.TextChoices):
    TEACHER = 'teacher', 'Giảng viên'
    STUDENT = 'student', 'Sinh viên'


class GenderChoice(models.TextChoices):
    MALE = 'male', 'Nam'
    FEMALE = 'female', 'Nữ'


class User(AbstractUser):
    gender = models.CharField(choices=GenderChoice.choices, max_length=10, null=True)
    role = models.CharField(max_length=10, choices=RoleChoice.choices)
    avatar = CloudinaryField(null=True)


class InstructorProfile(models.Model):
    document = CloudinaryField(null=False)
    bank_account = models.CharField(max_length=50, null=True)
    expertise = models.CharField(max_length=255)

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


class Course(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    intro_video = CloudinaryField(resource_type="video", null=False)
    active = models.BooleanField(default=True)
    image = CloudinaryField(null=False)

    instructor = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        unique_together = ('title', 'category')
        ordering = ['-created_date']


    def __str__(self):
        return self.title


class EnrollmentStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Chưa học"
    ENROLLED = "enrolled", "Đang học"
    COMPLETED = "completed", "Hoàn thành"


class Enrollment(BaseModel):
    enrolled_date = models.DateTimeField(auto_now_add=True)
    process_percent = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.NOT_STARTED)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ('user', 'course')


class Lesson(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    thumbnail = CloudinaryField(null=False)
    video = CloudinaryField(resource_type="video", null=False)
    active = models.BooleanField(default=True)
    duration = models.IntegerField(null=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')

    class Meta:
        unique_together = ('name', 'course')
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

class LessonCompleted(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('lesson', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.name}"

class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Đang chờ thanh toán"
    SUCCESS = "success", "Thanh toán thành công"
    FAILED = "failed", "Thanh toán thất bại"
    CANCELED = "canceled", "Đã hủy"

class Transaction(Interaction):
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING, null=True
    )

    def __str__(self):
        return self.amount.__str__() if self.amount else "No amount"