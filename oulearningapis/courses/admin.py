from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from courses.models import Category, Course, Lesson, Tag, Review
from django import forms

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Review)
