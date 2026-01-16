from rest_framework.pagination import LimitOffsetPagination


class CoursePagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

class CategoryPagination(LimitOffsetPagination):
    default_limit = 10


class ReviewPagination(LimitOffsetPagination):
    default_limit = 20

class LessonPagination(LimitOffsetPagination):
    default_limit = 20


class StudentPagination(LimitOffsetPagination):
    default_limit = 20


class TransactionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100
