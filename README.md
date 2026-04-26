# OU Learning API

OU Learning API là hệ thống backend xây dựng bằng Django phục vụ quản lý khóa học, bài học và tiến trình học tập cho sinh viên Đại học Mở.

## Tính năng chính

- Quản lý khóa học (Courses)
- Quản lý bài học (Lessons)
- Theo dõi tiến trình học tập của sinh viên
- Phân quyền truy cập cho người dùng
- API RESTful cho frontend hoặc ứng dụng di động

## Cấu trúc dự án

```
oulearningapis/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── courses/
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py
│   ├── models.py
│   ├── paginator.py
│   ├── perms.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
│       └── ...
├── oulearningapis/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
```

## Cài đặt

1. Clone repository:
	```
	git clone <repo-url>
	cd OU_Learning_API
	```

2. Tạo môi trường ảo và cài đặt các package:
	```
	python -m venv venv
	venv\Scripts\activate
	pip install -r requirements.txt
	```

3. Chạy migrate database:
	```
	python oulearningapis/manage.py migrate
	```

4. Chạy server:
	```
	python oulearningapis/manage.py runserver
	```

5. Truy cập API tại: `http://127.0.0.1:8000/`

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo pull request hoặc issue để thảo luận thêm.

## Giấy phép

Dự án này sử dụng giấy phép MIT.