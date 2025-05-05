# Tài liệu các thành phần UI - Ứng dụng Lên Thực Đơn Tuần

## 1. Tổng quan

Ứng dụng sử dụng PyQt5 để xây dựng giao diện người dùng. Các thành phần UI được tổ chức trong thư mục `ui/` và được quản lý bởi `MainWindow` trong `main_window.py`.

## 2. Các thành phần chính

### 2.1. MainWindow
**File:** `ui/main_window.py`

**Mô tả:**
- Cửa sổ chính của ứng dụng
- Quản lý các panel con
- Xử lý các sự kiện chung

**Các thành phần:**
- Menu bar
- Status bar
- Central widget (chứa các panel)
- Toolbar

### 2.2. MenuPanel
**File:** `ui/menu_panel.py`

**Mô tả:**
- Hiển thị và quản lý thực đơn
- Cho phép chỉnh sửa thực đơn
- Hiển thị danh sách mua sắm

**Các thành phần:**
- Bảng thực đơn theo ngày
- Form chỉnh sửa món ăn
- Danh sách mua sắm
- Nút tạo thực đơn mới

### 2.3. PreferencesPanel
**File:** `ui/preferences_panel.py`

**Mô tả:**
- Quản lý sở thích ẩm thực
- Lưu trữ thông tin về dị ứng và hạn chế ăn uống

**Các thành phần:**
- Form nhập sở thích
- Danh sách nguyên liệu yêu thích/không thích
- Danh sách món ăn yêu thích/không thích
- Form thông tin dị ứng và hạn chế

### 2.4. BudgetPanel
**File:** `ui/budget_panel.py`

**Mô tả:**
- Quản lý ngân sách cho thực đơn
- Hiển thị thống kê chi tiêu

**Các thành phần:**
- Slider chọn ngân sách
- Hiển thị ngân sách theo ngày/tuần
- Biểu đồ thống kê chi tiêu
- Cảnh báo vượt ngân sách

### 2.5. CuisinePanel
**File:** `ui/cuisine_panel.py`

**Mô tả:**
- Lựa chọn phong cách ẩm thực
- Hiển thị thông tin về các phong cách ẩm thực

**Các thành phần:**
- Danh sách phong cách ẩm thực
- Mô tả chi tiết từng phong cách
- Hình ảnh minh họa
- Nút chọn phong cách

## 3. Các dialog

### 3.1. APIKeyDialog
**Mô tả:**
- Dialog nhập API key
- Xác thực API key

### 3.2. ErrorDialog
**Mô tả:**
- Hiển thị thông báo lỗi
- Cung cấp thông tin chi tiết về lỗi

### 3.3. ConfirmationDialog
**Mô tả:**
- Xác nhận các hành động quan trọng
- Cảnh báo trước khi xóa dữ liệu

## 4. Custom Widgets

### 4.1. DishCard
**Mô tả:**
- Hiển thị thông tin một món ăn
- Cho phép chỉnh sửa nhanh

### 4.2. IngredientList
**Mô tả:**
- Hiển thị danh sách nguyên liệu
- Hỗ trợ thêm/xóa/sửa nguyên liệu

### 4.3. BudgetChart
**Mô tả:**
- Hiển thị biểu đồ ngân sách
- Tương tác với dữ liệu ngân sách

## 5. Styling

### 5.1. Theme
- Sử dụng Fusion style mặc định
- Tùy chỉnh màu sắc và font chữ
- Hỗ trợ dark/light mode

### 5.2. Responsive Design
- Tự động điều chỉnh kích thước
- Hỗ trợ nhiều độ phân giải màn hình
- Tối ưu cho cả desktop và laptop

## 6. Event Handling

### 6.1. Signals và Slots
- Sử dụng Qt's signal-slot mechanism
- Xử lý các sự kiện người dùng
- Cập nhật UI theo thời gian thực

### 6.2. Thread Safety
- Sử dụng QThread cho các tác vụ nặng
- Tránh block UI thread
- Xử lý lỗi bất đồng bộ 