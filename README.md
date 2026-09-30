# SkillMatch Backend

REST API cho SkillMatch — nền tảng kết nối sinh viên với cơ hội việc làm. Backend cung cấp xác thực JWT/Google, quản lý hồ sơ, CV, kỹ năng, tuyển dụng, ứng tuyển, thông báo và gợi ý công việc.

## Mục lục

- [Tính năng](#tính-năng)
- [Công nghệ](#công-nghệ)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Biến môi trường](#biến-môi-trường)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Xác thực và phân quyền](#xác-thực-và-phân-quyền)
- [API](#api)
- [Kiểm tra](#kiểm-tra)
- [Lưu ý bảo mật](#lưu-ý-bảo-mật)

## Tính năng

- Đăng ký và đăng nhập bằng JWT.
- Google Sign-In, bao gồm liên kết local account với Google account.
- Quên mật khẩu bằng token một lần, chỉ lưu hash token trong database.
- Quản lý student/recruiter profile, company, CV và kỹ năng.
- Quản lý job, job skill và application theo quyền recruiter/student.
- Tự động gửi notification khi application được chấp nhận hoặc từ chối.
- Recommendation kết hợp TF-IDF và đối sánh kỹ năng, trả về kỹ năng khớp và còn thiếu.

## Công nghệ

| Thành phần | Công nghệ |
| --- | --- |
| Web framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Authentication | JWT (`PyJWT`), `pwdlib` (Argon2) |
| Google authentication | `google-auth` |
| API documentation | OpenAPI / Swagger UI |

## Bắt đầu nhanh

### Yêu cầu

- Python 3.11+
- PostgreSQL 14+ (khuyến nghị)
- Google OAuth Client ID nếu dùng Google Sign-In

### 1. Clone và cài dependency

```powershell
git clone <repository-url>
cd Backend

py -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Tạo `.env` tại thư mục gốc theo mẫu ở phần [Biến môi trường](#biến-môi-trường).

### 3. Khởi tạo database

```powershell
.\.venv\Scripts\python -m app.create_tables
```

Lệnh này tạo bảng còn thiếu và bổ sung các cột xác thực Google cho database đã tồn tại.

### 4. Chạy server

```powershell
.\.venv\Scripts\uvicorn app.main:app --reload
```

Sau khi chạy:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Biến môi trường

Không commit `.env`. Các biến bắt buộc và tùy chọn:

```dotenv
# Required
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/skillmatch
JWT_SECRET_KEY=replace-with-a-long-random-secret

# Optional: Google Sign-In
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Required for CV PDF upload
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_STORAGE_BUCKET=cvs
# Optional when the bucket uses a custom public URL
SUPABASE_STORAGE_PUBLIC_URL=https://your-project.supabase.co/storage/v1/object/public/cvs

# Optional: password-reset email
FRONTEND_RESET_PASSWORD_URL=http://localhost:3000/reset-password
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=no-reply@example.com
```

`SMTP_*` là tùy chọn cho môi trường development. Khi chưa cấu hình SMTP, endpoint quên mật khẩu vẫn trả về phản hồi chung để tránh lộ email có tồn tại hay không.

## Cấu trúc dự án

```text
app/
├── core/           # Database, security và cấu hình chung
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic request/response schemas
├── routes/         # FastAPI route handlers
├── services/       # Dịch vụ tích hợp, ví dụ email
├── nlp/            # TF-IDF, xử lý văn bản và skill matching
├── create_tables.py
└── main.py         # FastAPI application và router registration
requirements.txt
```

## Xác thực và phân quyền

Các endpoint cần đăng nhập sử dụng HTTP Bearer token:

```http
Authorization: Bearer <access_token>
```

Hệ thống có hai role: `STUDENT` và `RECRUITER`.

- `STUDENT` có thể quản lý hồ sơ/CV/kỹ năng, ứng tuyển và xem notification của chính mình.
- `RECRUITER` có thể quản lý company, job, job skill và application thuộc company của mình.
- Notification được tạo bởi business logic của backend; không có public endpoint để tạo notification.

### Mật khẩu cho Google account

`PUT /api/v1/auth/password` phục vụ cả hai luồng:

| Loại tài khoản | Request body |
| --- | --- |
| Local account | `current_password` và `new_password` |
| Google-only account | Chỉ `new_password` để đặt mật khẩu local lần đầu |

Ví dụ đổi mật khẩu local account:

```json
{
  "current_password": "old-password",
  "new_password": "new-password-at-least-8-characters"
}
```

Sau khi Google-only account đặt mật khẩu, `auth_provider` trở thành `local+google`. Frontend có thể dùng `GET /api/v1/auth/me` và trường `has_password` để hiển thị đúng luồng.

## API

Base URL: `/api/v1`

Swagger UI là tài liệu chi tiết và luôn phản ánh request/response mới nhất: [`/docs`](http://127.0.0.1:8000/docs).

| Nhóm | Endpoints |
| --- | --- |
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/google`, `GET /auth/me`, `PUT /auth/password` |
| Password reset | `POST /auth/forgot-password`, `POST /auth/reset-password` |
| Profiles | `GET, PUT /students/profile`, `GET, PUT /recruiters/profile` |
| Companies | `POST /companies`, `GET, PUT, DELETE /companies/{company_id}` |
| CV | `GET, POST, PUT, DELETE /cvs`, `PATCH /cvs/{cv_id}/default` |
| Student skills | `GET, POST /skills/skills`, `PUT, DELETE /skills/skills/{skill_id}` |
| Jobs | `GET, POST /jobs`, `GET, PUT, DELETE /jobs/{job_id}`, `GET /jobs/search`, `PATCH /jobs/{job_id}/status` |
| Job skills | `GET /jobs/job_skills`, `GET, POST /jobs/{job_id}/skills`, `PUT, DELETE /jobs/{job_id}/skills/{skill_id}` |
| Applications | `POST /applications`, `GET /applications/{application_id}`, `GET /jobs/{job_id}/applications`, `PATCH /applications/{application_id}/status` |
| Recommendations | `GET /recommendations`, `POST /recommendations/generate`, `GET /recommendations/{recommendation_id}` |
| Notifications | `GET /notifications`, `PATCH /notifications/{notification_id}/read` |

### Ví dụ đăng nhập

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "your-password"
}
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user_id": 1,
  "email": "student@example.com",
  "role": "STUDENT"
}
```

## Recommendation flow

1. Student upload PDF bằng `multipart/form-data` tới `POST /api/v1/cvs` với field `file` và tùy chọn `is_default`.
2. Backend lưu PDF trên Supabase Storage, lưu URL vào `file_url` và text trích xuất bằng PyMuPDF vào `parsed_text`.
3. `POST /api/v1/recommendations/generate` lấy những job có trạng thái `OPEN`.
4. Điểm TF-IDF từ CV/job được kết hợp với skill matching theo tỷ trọng 40/60.
5. API trả về điểm, lý do, `matched_skills` và `missing_skills`.

## Kiểm tra

Kiểm tra cú pháp toàn bộ backend:

```powershell
.\.venv\Scripts\python -m compileall -q app
```

Kiểm tra server sinh OpenAPI thành công:

```powershell
.\.venv\Scripts\python -c "import importlib; print(importlib.import_module('app.main').app.openapi()['openapi'])"
```

## Lưu ý bảo mật

- Giữ `.env`, secret JWT, SMTP credentials và database credentials ngoài Git.
- Dùng `JWT_SECRET_KEY` dài, ngẫu nhiên và khác nhau giữa development/staging/production.
- Triển khai production qua HTTPS và cấu hình CORS phù hợp cho frontend.
- Không trả token reset mật khẩu từ API hoặc ghi raw reset token vào database/log.
