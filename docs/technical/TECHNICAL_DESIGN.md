# Tài liệu thiết kế kỹ thuật - Ứng dụng Lên Thực Đơn Tuần

## 1. Tổng quan

Ứng dụng Lên Thực Đơn Tuần là một ứng dụng desktop được phát triển bằng Python, sử dụng PyQt5 cho giao diện người dùng và OpenAI API để tạo thực đơn thông minh. Ứng dụng giúp người dùng lập kế hoạch thực đơn tuần dựa trên sở thích cá nhân, ngân sách và thời gian chuẩn bị.

## 2. Kiến trúc hệ thống

### 2.1. Cấu trúc thư mục
```
LenThucDonTuan/
├── api/                 # Xử lý API và prompts
├── database/           # Quản lý database
├── ui/                 # Giao diện người dùng
├── utils/              # Các tiện ích hỗ trợ
├── main.py            # Điểm khởi đầu ứng dụng
├── config.py          # Cấu hình ứng dụng
└── requirements.txt    # Các dependencies
```

### 2.2. Luồng dữ liệu
```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Database
    participant OpenAIAPI
    participant IngredientOptimizer

    User->>UI: Nhập sở thích, ngân sách, thời gian
    UI->>Database: Lưu thông tin
    UI->>OpenAIAPI: Gửi yêu cầu tạo thực đơn
    OpenAIAPI-->>UI: Trả về thực đơn
    UI->>IngredientOptimizer: Tối ưu hóa nguyên liệu
    IngredientOptimizer-->>UI: Trả về thực đơn tối ưu
    UI->>Database: Lưu thực đơn cuối cùng
    UI-->>User: Hiển thị kết quả
```

### 2.3. Kiến trúc tổng thể
```mermaid
graph TD
    A[Main Window] --> B[Menu Panel]
    A --> C[Preferences Panel]
    A --> D[Budget Panel]
    A --> E[Cuisine Panel]
    
    B --> F[Database]
    C --> F
    D --> F
    E --> F
    
    B --> G[OpenAI API]
    C --> G
    D --> G
    E --> G
    
    B --> H[Ingredient Optimizer]
    H --> F
```

## 3. Các thành phần chính

### 3.1. Giao diện người dùng (UI)
```mermaid
classDiagram
    class MainWindow {
        +QMenuBar menuBar
        +QStatusBar statusBar
        +QToolBar toolBar
        +QWidget centralWidget
        +setupUI()
        +handleEvents()
    }
    
    class MenuPanel {
        +QTableWidget menuTable
        +QFormLayout editForm
        +QListWidget shoppingList
        +QPushButton createButton
        +displayMenu()
        +editDish()
        +generateShoppingList()
    }
    
    class PreferencesPanel {
        +QFormLayout preferencesForm
        +QListWidget likedIngredients
        +QListWidget dislikedIngredients
        +QListWidget likedDishes
        +QListWidget dislikedDishes
        +savePreferences()
        +loadPreferences()
    }
    
    class BudgetPanel {
        +QSlider budgetSlider
        +QLabel budgetLabel
        +QChart budgetChart
        +updateBudget()
        +displayStatistics()
    }
    
    class CuisinePanel {
        +QComboBox cuisineList
        +QLabel descriptionLabel
        +QLabel imageLabel
        +QPushButton selectButton
        +loadCuisines()
        +selectCuisine()
    }
    
    MainWindow --> MenuPanel
    MainWindow --> PreferencesPanel
    MainWindow --> BudgetPanel
    MainWindow --> CuisinePanel
```

### 3.2. Xử lý API
```mermaid
sequenceDiagram
    participant UI
    participant APIKeyManager
    participant OpenAIAPI
    participant PromptTemplates
    
    UI->>APIKeyManager: Lấy API key
    APIKeyManager-->>UI: Trả về API key
    UI->>OpenAIAPI: Gửi request
    OpenAIAPI->>PromptTemplates: Lấy template
    PromptTemplates-->>OpenAIAPI: Trả về template
    OpenAIAPI->>OpenAIAPI: Gọi API
    OpenAIAPI-->>UI: Trả về kết quả
```

### 3.3. Database
```mermaid
erDiagram
    users ||--o{ preferences : has
    users ||--o{ menus : creates
    menus ||--o{ menu_items : contains
    menus ||--|| shopping_lists : generates
    
    users {
        int id PK
        string name
        timestamp created_at
    }
    
    preferences {
        int id PK
        int user_id FK
        string liked_ingredients
        string disliked_ingredients
        string liked_dishes
        string disliked_dishes
        string allergies
        string dietary_restrictions
        timestamp created_at
    }
    
    menus {
        int id PK
        int user_id FK
        string name
        float budget
        int prep_time
        string cuisine_type
        timestamp created_at
    }
    
    menu_items {
        int id PK
        int menu_id FK
        string day
        string meal_type
        string dish_name
        string ingredients
        int prep_time
        float cost
    }
    
    shopping_lists {
        int id PK
        int menu_id FK
        string ingredients
        float total_cost
        timestamp created_at
    }
```

### 3.4. Tiện ích
```mermaid
classDiagram
    class APIKeyManager {
        +string get_api_key()
        +bool save_api_key(string key)
        +bool validate_api_key(string key)
    }
    
    class IngredientOptimizer {
        +dict optimize_ingredients(dict menu)
        +dict generate_shopping_list(dict menu)
        +float calculate_total_cost(dict menu)
    }
    
    class Helpers {
        +string format_currency(float amount)
        +string format_time(int minutes)
        +bool validate_input(dict data)
        +string sanitize_output(string text)
    }
```

## 4. Công nghệ sử dụng

- Python 3.8+
- PyQt5: Giao diện người dùng
- SQLite: Database
- OpenAI API: Tạo thực đơn thông minh
- Cryptography: Mã hóa API key

## 5. Bảo mật

- API key được mã hóa và lưu trữ an toàn
- Dữ liệu người dùng được lưu trữ cục bộ
- Không có thông tin nhạy cảm nào được gửi lên server

## 6. Hiệu suất

- Sử dụng caching cho các request API
- Tối ưu hóa database queries
- Xử lý bất đồng bộ cho các tác vụ nặng

## 7. Mở rộng

- Dễ dàng thêm các phong cách ẩm thực mới
- Có thể tích hợp thêm các API khác
- Hỗ trợ đa ngôn ngữ 