# Hướng dẫn phát triển - Ứng dụng Lên Thực Đơn Tuần

## 1. Thiết lập môi trường phát triển

### 1.1. Yêu cầu hệ thống
- Python 3.8+
- Git
- IDE hỗ trợ Python (VS Code, PyCharm, etc.)

### 1.2. Cài đặt
```bash
# Clone repository
git clone https://github.com/yourusername/LenThucDonTuan.git
cd LenThucDonTuan

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 1.3. Cấu hình
1. Tạo file `.env` từ `example.env`
2. Thêm OpenAI API key vào `.env`
3. Cấu hình các tham số khác trong `config.py`

## 2. Cấu trúc project

### 2.1. Thư mục
```
LenThucDonTuan/
├── api/                 # Xử lý API
├── database/           # Quản lý database
├── ui/                 # Giao diện người dùng
├── utils/              # Các tiện ích
├── tests/              # Unit tests
└── docs/              # Tài liệu
```

### 2.2. Quy ước đặt tên
- Tên file: snake_case
- Tên class: PascalCase
- Tên biến/functions: snake_case
- Tên constants: UPPER_CASE

## 3. Quy trình phát triển

### 3.1. Git Workflow
1. Tạo branch mới từ `develop`
2. Phát triển tính năng
3. Tạo pull request
4. Code review
5. Merge vào `develop`

### 3.2. Commit Message
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- feat: Tính năng mới
- fix: Sửa lỗi
- docs: Thay đổi tài liệu
- style: Thay đổi format
- refactor: Tái cấu trúc code
- test: Thêm/sửa test
- chore: Cập nhật build tools

### 3.3. Code Review
- Kiểm tra code style
- Đảm bảo test coverage
- Review security
- Kiểm tra performance

## 4. Testing

### 4.1. Unit Tests
```bash
# Chạy tất cả tests
python -m pytest

# Chạy test với coverage
python -m pytest --cov=.
```

### 4.2. Test Cases
- Test API calls
- Test database operations
- Test UI components
- Test utility functions

## 5. Debugging

### 5.1. Logging
- Sử dụng module `logging`
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log file: `app.log`

### 5.2. Debug Tools
- PyCharm debugger
- VS Code debugger
- pdb/ipdb

## 6. Deployment

### 6.1. Build
```bash
# Tạo executable
pyinstaller main.spec
```

### 6.2. Release
1. Tăng version trong `config.py`
2. Cập nhật CHANGELOG.md
3. Tạo release tag
4. Build và upload release

## 7. Bảo trì

### 7.1. Database Migration
1. Tạo migration script
2. Backup database
3. Chạy migration
4. Verify data

### 7.2. Performance Optimization
- Profile code
- Optimize database queries
- Cache API responses
- Minimize UI updates

## 8. Security

### 8.1. API Key
- Mã hóa API key
- Không commit API key
- Rotate key định kỳ

### 8.2. Data Protection
- Validate input
- Sanitize output
- Use prepared statements
- Encrypt sensitive data

## 9. Troubleshooting

### 9.1. Common Issues
- API key không hợp lệ
- Database connection error
- UI freezing
- Memory leaks

### 9.2. Solutions
- Check logs
- Verify configuration
- Clear cache
- Restart application 