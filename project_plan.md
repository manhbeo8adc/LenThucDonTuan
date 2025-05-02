# Kế hoạch phát triển ứng dụng lên thực đơn tuần

## Tổng quan

Ứng dụng sẽ giúp người dùng lên thực đơn cho cả tuần dựa trên sở thích cá nhân, ngân sách, thời gian chuẩn bị và tối ưu hóa nguyên liệu. Ứng dụng sẽ sử dụng API của ChatGPT để tạo ra các gợi ý món ăn phù hợp.

## Các tính năng chính

1. **Quản lý sở thích cá nhân**:
   - Nguyên liệu yêu thích
   - Nguyên liệu không thích
   - Món ăn yêu thích
   - Món ăn không thích

2. **Lựa chọn phong cách ẩm thực**:
   - Ẩm thực miền Nam Việt Nam
   - Ẩm thực miền Bắc Việt Nam
   - Ẩm thực Pháp
   - Và các loại ẩm thực khác...

3. **Giới hạn chi phí**:
   - Thiết lập ngân sách cho mỗi bữa ăn (ví dụ: 70k/bữa, 100k/bữa,...)

4. **Thời gian chuẩn bị**:
   - Lựa chọn thời gian tối đa cho việc chuẩn bị (1 giờ, 2 giờ,...)

5. **Tối ưu hóa nguyên liệu**:
   - Tận dụng nguyên liệu thừa từ các bữa trước đó
   - Đề xuất các món ăn có thể sử dụng chung nguyên liệu

6. **Giao diện người dùng**:
   - Giao diện thân thiện, dễ sử dụng
   - Khả năng chỉnh sửa, thêm/xóa món ăn trong thực đơn
   - Hiển thị thực đơn theo ngày trong tuần

## Công nghệ sử dụng

- **Ngôn ngữ lập trình**: Python 3.8+
- **Giao diện người dùng**: PyQt6 hoặc Tkinter
- **API**: OpenAI ChatGPT API
- **Cơ sở dữ liệu**: SQLite (để lưu trữ sở thích người dùng và lịch sử thực đơn)

## Các bước triển khai

### 1. Thiết lập môi trường (1-2 ngày)

- Cài đặt Python
- Cài đặt các thư viện cần thiết:
  - `openai`: Kết nối với API của ChatGPT
  - `PyQt6`/`Tkinter`: Xây dựng giao diện người dùng
  - `sqlite3`: Quản lý cơ sở dữ liệu
  - `pandas`: Xử lý dữ liệu
- Đăng ký tài khoản OpenAI và lấy API key

### 2. Xây dựng cơ sở dữ liệu (2-3 ngày)

- Thiết kế schema cơ sở dữ liệu:
  - Bảng lưu thông tin người dùng và sở thích
  - Bảng lưu thông tin nguyên liệu
  - Bảng lưu thông tin món ăn
  - Bảng lưu thực đơn đã tạo

### 3. Phát triển API wrapper (2-3 ngày)

- Xây dựng lớp kết nối với OpenAI API
- Thiết kế prompt template để tạo ra thực đơn
- Tối ưu hóa prompt tuning để cải thiện kết quả

### 4. Xây dựng giao diện người dùng (5-7 ngày)

- Thiết kế layout chính của ứng dụng
- Xây dựng các màn hình:
  - Màn hình thiết lập sở thích
  - Màn hình lựa chọn phong cách ẩm thực
  - Màn hình cài đặt ngân sách và thời gian
  - Màn hình hiển thị thực đơn tuần
  - Màn hình chỉnh sửa thực đơn

### 5. Tích hợp các thành phần (3-4 ngày)

- Kết nối giao diện người dùng với API wrapper
- Tích hợp cơ sở dữ liệu với các thành phần khác
- Xây dựng logic tối ưu hóa nguyên liệu

### 6. Kiểm thử và tối ưu hóa (3-5 ngày)

- Kiểm thử tính năng
- Sửa lỗi và tối ưu hóa hiệu suất
- Cải thiện giao diện người dùng dựa trên phản hồi

### 7. Đóng gói và triển khai (1-2 ngày)

- Tạo tệp cài đặt cho người dùng cuối
- Viết tài liệu hướng dẫn sử dụng
- Triển khai ứng dụng

## Cấu trúc dự án

```
LenThucDonTuan/
├── README.md                 # Tài liệu hướng dẫn
├── requirements.txt          # Các thư viện cần thiết
├── main.py                   # Điểm khởi đầu của ứng dụng
├── config.py                 # Cấu hình ứng dụng
├── database/
│   ├── __init__.py
│   ├── models.py             # Định nghĩa các mô hình dữ liệu
│   └── db_manager.py         # Quản lý cơ sở dữ liệu
├── api/
│   ├── __init__.py
│   ├── openai_api.py         # Kết nối với API OpenAI
│   └── prompt_templates.py   # Các mẫu prompt
├── ui/
│   ├── __init__.py
│   ├── main_window.py        # Cửa sổ chính
│   ├── preferences_panel.py  # Panel thiết lập sở thích
│   ├── cuisine_panel.py      # Panel lựa chọn ẩm thực
│   ├── budget_panel.py       # Panel cài đặt ngân sách
│   ├── menu_panel.py         # Panel hiển thị thực đơn
│   └── resources/            # Tài nguyên UI (icons, etc.)
└── utils/
    ├── __init__.py
    ├── ingredient_optimizer.py  # Tối ưu hóa nguyên liệu
    └── helpers.py            # Các hàm tiện ích
```

## Hướng dẫn sử dụng prompt tuning

Để tạo ra prompt hiệu quả cho ChatGPT API, cần cung cấp các thông tin sau:

1. **Thông tin rõ ràng về sở thích**:
   ```
   "Tôi thích [nguyên liệu yêu thích], không thích [nguyên liệu không thích]."
   "Tôi thích ăn [món ăn yêu thích], không thích [món ăn không thích]."
   ```

2. **Phong cách ẩm thực**:
   ```
   "Hãy gợi ý các món ăn theo phong cách [loại ẩm thực]."
   ```

3. **Giới hạn ngân sách**:
   ```
   "Mỗi bữa ăn không quá [số tiền] VND."
   ```

4. **Thời gian chuẩn bị**:
   ```
   "Thời gian chuẩn bị không quá [số giờ] giờ."
   ```

5. **Tối ưu nguyên liệu**:
   ```
   "Hãy đề xuất các món có thể tận dụng nguyên liệu thừa từ các bữa trước."
   "Bữa trước đã sử dụng [nguyên liệu đã sử dụng], hãy đề xuất món ăn có thể tận dụng phần còn lại."
   ```

## Các thách thức có thể gặp phải

1. **Giới hạn của API**: API của ChatGPT có thể có giới hạn về số lượng request hoặc token, cần xây dựng cơ chế cache để giảm thiểu số lượng request.

2. **Chất lượng prompt**: Kết quả từ ChatGPT phụ thuộc nhiều vào chất lượng của prompt, cần liên tục tối ưu prompt để có kết quả tốt.

3. **Xử lý phản hồi**: Phản hồi từ API có thể không theo đúng format mong muốn, cần xây dựng cơ chế parse và xử lý lỗi.

4. **Tính chính xác của chi phí**: Việc ước tính chi phí cho mỗi món ăn cần có dữ liệu về giá nguyên liệu, có thể cần cập nhật thường xuyên.

## Kế hoạch mở rộng tương lai

1. **Xuất/nhập thực đơn**: Cho phép người dùng lưu và chia sẻ thực đơn.

2. **Tạo danh sách mua sắm**: Tự động tạo danh sách nguyên liệu cần mua dựa trên thực đơn.

3. **Thông tin dinh dưỡng**: Hiển thị thông tin dinh dưỡng của các món ăn.

4. **Gợi ý món ăn theo mùa**: Đề xuất món ăn phù hợp với mùa trong năm.

5. **Tích hợp với các dịch vụ giao hàng**: Cho phép đặt nguyên liệu trực tiếp từ ứng dụng.

## Các câu hỏi cần làm rõ

1. Bạn đã có tài khoản OpenAI và API key chưa?
2. Bạn muốn ứng dụng có giao diện đồ họa như thế nào? (đơn giản hay phức tạp)
3. Bạn muốn lưu trữ dữ liệu người dùng như thế nào? (cục bộ hay đám mây)
4. Bạn có yêu cầu cụ thể về ngôn ngữ hiển thị trong ứng dụng không? (tiếng Việt, tiếng Anh)
5. Bạn có muốn thêm tính năng chia sẻ thực đơn với người khác không?
6. Bạn có nhu cầu thêm công thức chi tiết của món ăn không? 