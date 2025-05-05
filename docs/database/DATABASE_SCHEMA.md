# Tài liệu cấu trúc Database - Ứng dụng Lên Thực Đơn Tuần

## 1. Tổng quan

Ứng dụng sử dụng SQLite làm database, lưu trữ tại `%APPDATA%/LenThucDonTuan/data.db`. Database được quản lý bởi `DBManager` trong module `database/db_manager.py`.

## 2. Các bảng

### 2.1. Bảng `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Mô tả:**
- Lưu trữ thông tin người dùng
- Mỗi người dùng có một ID duy nhất
- Hiện tại chỉ lưu tên người dùng

### 2.2. Bảng `preferences`
```sql
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    liked_ingredients TEXT,
    disliked_ingredients TEXT,
    liked_dishes TEXT,
    disliked_dishes TEXT,
    allergies TEXT,
    dietary_restrictions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Mô tả:**
- Lưu trữ sở thích ẩm thực của người dùng
- Mỗi người dùng có thể có nhiều bản ghi sở thích
- Các trường TEXT lưu dưới dạng JSON string

### 2.3. Bảng `menus`
```sql
CREATE TABLE menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    budget REAL NOT NULL,
    prep_time INTEGER NOT NULL,
    cuisine_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Mô tả:**
- Lưu trữ thông tin chung về thực đơn
- Mỗi thực đơn thuộc về một người dùng
- Lưu ngân sách, thời gian chuẩn bị và loại ẩm thực

### 2.4. Bảng `menu_items`
```sql
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    dish_name TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    prep_time INTEGER NOT NULL,
    cost REAL NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menus(id)
);
```

**Mô tả:**
- Lưu trữ chi tiết các món ăn trong thực đơn
- Mỗi món ăn thuộc về một thực đơn
- Lưu thông tin về nguyên liệu, thời gian chuẩn bị và chi phí

### 2.5. Bảng `shopping_lists`
```sql
CREATE TABLE shopping_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    ingredients TEXT NOT NULL,
    total_cost REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus(id)
);
```

**Mô tả:**
- Lưu trữ danh sách mua sắm cho mỗi thực đơn
- Mỗi danh sách thuộc về một thực đơn
- Lưu tổng chi phí và danh sách nguyên liệu dưới dạng JSON

## 3. Quan hệ giữa các bảng

```
users
  |
  |-- preferences (1:N)
  |
  |-- menus (1:N)
       |
       |-- menu_items (1:N)
       |
       |-- shopping_lists (1:1)
```

## 4. Indexes

```sql
CREATE INDEX idx_preferences_user_id ON preferences(user_id);
CREATE INDEX idx_menus_user_id ON menus(user_id);
CREATE INDEX idx_menu_items_menu_id ON menu_items(menu_id);
CREATE INDEX idx_shopping_lists_menu_id ON shopping_lists(menu_id);
```

## 5. Triggers

```sql
-- Trigger để tự động cập nhật thời gian tạo
CREATE TRIGGER update_created_at
AFTER UPDATE ON users
BEGIN
    UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

## 6. Backup và Recovery

- Database được backup tự động mỗi ngày
- Backup files được lưu tại `%APPDATA%/LenThucDonTuan/backups/`
- Tối đa 7 bản backup được lưu giữ
- Có thể khôi phục từ backup thông qua giao diện quản trị 