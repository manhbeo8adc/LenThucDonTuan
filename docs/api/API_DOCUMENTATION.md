# Tài liệu API - Ứng dụng Lên Thực Đơn Tuần

## 1. OpenAI API Integration

### 1.1. Cấu hình
- Model: gpt-4.1-mini-2025-04-14
- API Key: Được lưu trữ an toàn trong file mã hóa
- Endpoint: https://api.openai.com/v1/chat/completions

### 1.2. Các API Endpoints

#### 1.2.1. Tạo thực đơn
```python
def generate_menu(
    preferences: Dict[str, Any],
    budget: float,
    prep_time: int,
    cuisine_type: str
) -> Dict[str, Any]
```

**Parameters:**
- `preferences`: Dictionary chứa sở thích người dùng
- `budget`: Ngân sách cho mỗi bữa ăn (VND)
- `prep_time`: Thời gian chuẩn bị tối đa (phút)
- `cuisine_type`: Loại ẩm thực

**Response:**
```json
{
    "success": true,
    "menu": {
        "monday": {
            "breakfast": {
                "name": "Tên món",
                "ingredients": ["nguyên liệu 1", "nguyên liệu 2"],
                "prep_time": 30,
                "cost": 50000
            },
            "lunch": {...},
            "dinner": {...}
        },
        "tuesday": {...},
        ...
    }
}
```

#### 1.2.2. Tối ưu hóa nguyên liệu
```python
def optimize_ingredients(menu: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `menu`: Thực đơn cần tối ưu

**Response:**
```json
{
    "success": true,
    "optimized_menu": {...},
    "shopping_list": {
        "ingredients": [
            {
                "name": "Tên nguyên liệu",
                "quantity": "Số lượng",
                "unit": "Đơn vị"
            }
        ],
        "total_cost": 500000
    }
}
```

### 1.3. Error Handling

#### 1.3.1. Error Codes
- `400`: Bad Request - Thông tin đầu vào không hợp lệ
- `401`: Unauthorized - API key không hợp lệ
- `429`: Too Many Requests - Vượt quá giới hạn request
- `500`: Internal Server Error - Lỗi server

#### 1.3.2. Error Response
```json
{
    "success": false,
    "error": {
        "code": 400,
        "message": "Mô tả lỗi"
    }
}
```

## 2. Local API

### 2.1. Database API

#### 2.1.1. Lưu thực đơn
```python
def save_menu(menu: Dict[str, Any]) -> bool
```

#### 2.1.2. Lấy thực đơn
```python
def get_menu(menu_id: int) -> Dict[str, Any]
```

#### 2.1.3. Lưu sở thích
```python
def save_preferences(preferences: Dict[str, Any]) -> bool
```

#### 2.1.4. Lấy sở thích
```python
def get_preferences() -> Dict[str, Any]
```

### 2.2. Utility APIs

#### 2.2.1. API Key Management
```python
def save_api_key(key: str) -> bool
def get_api_key() -> str
```

#### 2.2.2. Ingredient Optimization
```python
def optimize_ingredients(menu: Dict[str, Any]) -> Dict[str, Any]
```

## 3. Rate Limiting

- OpenAI API: 3 requests/minute
- Local APIs: Không giới hạn

## 4. Security

- API key được mã hóa trước khi lưu
- Tất cả API calls đều được validate input
- Không lưu trữ thông tin nhạy cảm 