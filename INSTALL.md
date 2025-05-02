# Hướng dẫn cài đặt ứng dụng Lên Thực Đơn Tuần

## Yêu cầu hệ thống

- Python 3.8 hoặc cao hơn
- Pip (trình quản lý gói của Python)
- OpenAI API key

## Bước 1: Cài đặt Python và Pip

### Windows:

1. Tải Python từ [trang chủ Python](https://www.python.org/downloads/).
2. Trong quá trình cài đặt, đảm bảo tích chọn "Add Python to PATH".
3. Pip thường được cài đặt cùng với Python.

### macOS:

1. Sử dụng Homebrew để cài đặt Python:
```
brew install python
```

### Linux:

1. Sử dụng trình quản lý gói của hệ điều hành:
```
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

## Bước 2: Tải mã nguồn ứng dụng

1. Tải mã nguồn từ repository:
```
git clone https://github.com/yourusername/LenThucDonTuan.git
cd LenThucDonTuan
```

Hoặc tải file ZIP và giải nén.

## Bước 3: Cài đặt các thư viện phụ thuộc

1. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

## Bước 4: Cấu hình API key

1. Đăng ký tài khoản tại [OpenAI](https://platform.openai.com/) nếu bạn chưa có.
2. Tạo API key tại [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).
3. Tạo file `.env` trong thư mục gốc của ứng dụng và thêm API key của bạn:
```
OPENAI_API_KEY=your_api_key_here
```

## Bước 5: Chạy ứng dụng

1. Chạy ứng dụng bằng lệnh:
```
python main.py
```

## Xử lý sự cố

### Lỗi "ModuleNotFoundError"

Nếu bạn gặp lỗi "ModuleNotFoundError", hãy đảm bảo bạn đã cài đặt đầy đủ các thư viện:
```
pip install -r requirements.txt
```

### Lỗi "OPENAI_API_KEY environment variable not found"

Đảm bảo bạn đã tạo file `.env` với API key hợp lệ trong thư mục gốc của ứng dụng.

### Lỗi "sqlite3.OperationalError: unable to open database file"

Đảm bảo thư mục gốc của ứng dụng có quyền ghi.

## Cấu hình nâng cao

### Thay đổi model của OpenAI

Mặc định, ứng dụng sử dụng model "gpt-3.5-turbo". Nếu bạn muốn sử dụng model khác (như gpt-4), bạn có thể thay đổi giá trị `OPENAI_MODEL` trong file `config.py`.

### Thiết lập proxy

Nếu bạn cần sử dụng proxy để kết nối với API của OpenAI, bạn có thể thêm thiết lập proxy vào file `.env`:
```
HTTP_PROXY=http://proxy_address:port
HTTPS_PROXY=http://proxy_address:port
```

## Hỗ trợ

Nếu bạn gặp vấn đề khi cài đặt hoặc sử dụng ứng dụng, vui lòng tạo issue trên GitHub hoặc liên hệ qua email. 