# Ứng dụng lên thực đơn tuần

Ứng dụng giúp lập kế hoạch thực đơn tuần dựa trên sở thích cá nhân, ngân sách, và thời gian chuẩn bị, với tính năng tối ưu nguyên liệu giữa các bữa ăn.

## Tính năng

- Tạo thực đơn cho cả tuần dựa trên sở thích cá nhân
- Lựa chọn phong cách ẩm thực (miền Bắc, miền Nam, ẩm thực Pháp, ...)
- Giới hạn chi phí theo ngân sách cá nhân
- Giới hạn thời gian chuẩn bị
- Tối ưu hóa nguyên liệu giữa các bữa ăn
- Giao diện thân thiện, dễ sử dụng

## Yêu cầu

- Python 3.8+
- OpenAI API key

## Cài đặt

1. Clone repository:
```
git clone https://github.com/yourusername/LenThucDonTuan.git
cd LenThucDonTuan
```

2. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

3. Tạo file `.env` chứa API key của OpenAI:
```
OPENAI_API_KEY=your_api_key_here
```

4. Chạy ứng dụng:
```
python main.py
```

## Hướng dẫn sử dụng

1. Nhập sở thích cá nhân (nguyên liệu yêu thích/không thích, món ăn yêu thích/không thích)
2. Chọn phong cách ẩm thực
3. Thiết lập ngân sách và thời gian chuẩn bị
4. Nhấn nút "Tạo thực đơn" để nhận kết quả
5. Chỉnh sửa thực đơn nếu cần
6. Lưu hoặc xuất thực đơn

## Đóng góp

Mọi đóng góp đều được chào đón. Vui lòng tạo issue trước khi gửi pull request. 