from rest_framework.pagination import LimitOffsetPagination


class CoursePagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 20


class CategoryPagination(LimitOffsetPagination):
    default_limit = 15
    max_limit = 20


class ReviewPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 20
