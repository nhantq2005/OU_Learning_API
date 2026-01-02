from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.routers import DefaultRouter

r = routers.DefaultRouter()
r.register('categories', views.CategoryView, basename='category')
r.register('courses', views.CourseView, basename='course')
r.register('chapters', views.ChapterView, basename='chapter')
r.register('lessons', views.LessonView, basename='lesson')
r.register('tags', views.TagView, basename='tag')
r.register('reviews', views.ReviewView, basename='review')
r.register('users', views.UserView, basename='user')
r.register('enrollments', views.EnrollmentView, basename='enrollment')


urlpatterns = [
    path('', include(r.urls))
]
