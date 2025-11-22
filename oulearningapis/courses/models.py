# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from cloudinary.models import CloudinaryField
#
#
# class User(AbstractUser):
#     role = models.CharField(max_length=10)
#     is_verified = models.BooleanField(default=True)
#     avatar = CloudinaryField(null=True)
#
#
# class StatusChoice(models.TextChoices):
#     PENDING = 'PEN', 'Pending'
#     APPROVED = 'APP', 'Approved'
#     REJECTED = 'REJ', 'Rejected'
#
#
# class InstructorProfiles(models.Model):
#     document = CloudinaryField(null=False)
#     status = models.CharField(max_length=3, choices=StatusChoice.PENDING, default=StatusChoice.PENDING)
#     bank_account = models.CharField(null=True)
#     expertise = models.CharField(max_length=255)
#
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#
#
# class BaseModel(models.Model):
#     created_date = models.DateTimeField(auto_now_add=True)
#     updated_date = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         abstract = True
#
#
# class Category(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     image = CloudinaryField(null=False)
#     active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Tag(models.Model):
#     name = models.CharField(max_length=255)
#     active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Course(models.Model):
#     title = models.CharField(max_length=255)
#     description = models.TextField(null=False)
#     price = models.DecimalField(max_digits=10)
#     intro_video = CloudinaryField(null=False)
#     active = models.BooleanField(default=True)
#     image = CloudinaryField(null=False)
#     duration_minutes = models.FloatField()
#
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#
#
# class Enrollment(models.Model):
#     enrolled_date = models.DateTimeField()
#     process_percent = models.FloatField()
#     # status =
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#
#
# class Lesson(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(null=False)
#     thumbnail = CloudinaryField(null=False)
#     video = CloudinaryField(null=False)
#
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     tags = models.ManyToManyField(Tag)
#
#
# class Review(BaseModel):
#     rating = models.IntegerField()
#     comment = models.TextField()
#
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#
# # MO RONG
