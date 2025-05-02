"""
Prompt templates for OpenAI API requests.
"""

# System message for menu generation
MENU_SYSTEM_MESSAGE = """
Bạn là một đầu bếp chuyên nghiệp có nhiều kinh nghiệm trong việc lập thực đơn và tối ưu hóa 
nguyên liệu. Nhiệm vụ của bạn là tạo ra thực đơn cho cả tuần dựa trên sở thích cá nhân, 
ngân sách, và thời gian chuẩn bị. Hãy đảm bảo các món ăn phù hợp với phong cách ẩm thực 
được chọn và tối ưu hóa việc sử dụng nguyên liệu giữa các bữa.

Phản hồi của bạn phải ở định dạng JSON, theo cấu trúc được cung cấp.
"""

# Template for weekly menu generation
WEEKLY_MENU_TEMPLATE = """
Tạo thực đơn cho các ngày: {days} với các bữa ăn: {meals_per_day}.

Sở thích cá nhân:
- Nguyên liệu yêu thích: {favorite_ingredients}
- Nguyên liệu không thích: {disliked_ingredients}
- Món ăn yêu thích: {favorite_dishes}
- Món ăn không thích: {disliked_dishes}

Phong cách ẩm thực: {cuisine_type}
Ngân sách tối đa mỗi bữa: {budget_per_meal} VND
Thời gian chuẩn bị tối đa: {max_prep_time} phút

{optimization_instructions}

Hãy đưa ra những món ăn cụ thể cho từng bữa trong tuần, cố gắng tối ưu hóa nguyên liệu giữa các bữa ăn.
Ví dụ, nếu một bữa có món sử dụng bí đỏ, hãy đề xuất món khác sử dụng phần bí đỏ còn lại.

Trả về thực đơn dưới dạng JSON với cấu trúc như sau:
{
  "menu": {
    "Ngày 1": {
      "Bữa sáng": {
        "name": "Tên món ăn",
        "ingredients": ["nguyên liệu 1", "nguyên liệu 2", ...],
        "preparation_time": thời gian chuẩn bị (số phút),
        "estimated_cost": chi phí ước tính (VND),
        "reused_ingredients": ["nguyên liệu tái sử dụng 1", ...]
      },
      "Bữa trưa": { ... },
      "Bữa tối": { ... }
    },
    "Ngày 2": { ... },
    ...
  },
  "optimization_notes": [
    "Ghi chú về cách tối ưu hóa nguyên liệu giữa các bữa"
  ]
}
"""

# Template for ingredient optimization
OPTIMIZATION_TEMPLATE = """
Tối ưu hóa nguyên liệu:
Vui lòng đề xuất các món ăn có thể tận dụng nguyên liệu từ các bữa trước. 
Các món ăn đã chuẩn bị trước đó:
{previous_meals}
"""

# System message for recipe generation
RECIPE_SYSTEM_MESSAGE = """
Bạn là một đầu bếp chuyên nghiệp, cung cấp công thức nấu ăn chi tiết.
Hãy cung cấp công thức chi tiết cho món ăn được yêu cầu, bao gồm nguyên liệu,
các bước thực hiện, thời gian chuẩn bị và nấu, và các gợi ý bổ sung.

Phản hồi của bạn phải ở định dạng JSON, theo cấu trúc được cung cấp.
"""

# Template for recipe generation
RECIPE_TEMPLATE = """
Hãy cung cấp công thức chi tiết để nấu món {dish_name}{cuisine_str}.

Trả về công thức dưới dạng JSON với cấu trúc như sau:
{
  "recipe": {
    "name": "Tên món ăn",
    "cuisine_type": "Loại ẩm thực",
    "preparation_time": thời gian chuẩn bị (số phút),
    "cooking_time": thời gian nấu (số phút),
    "servings": số người ăn,
    "ingredients": [
      {"name": "tên nguyên liệu", "amount": "số lượng", "unit": "đơn vị"},
      ...
    ],
    "steps": [
      "Bước 1: ...",
      "Bước 2: ...",
      ...
    ],
    "tips": [
      "Mẹo 1: ...",
      "Mẹo 2: ...",
      ...
    ]
  }
}
""" 