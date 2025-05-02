"""
Configuration settings for the application.
"""
import os
from dotenv import load_dotenv
from utils.api_key_manager import get_api_key

# Load environment variables from .env file
load_dotenv()

# Get AppData path for Windows
APP_DATA = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'), 'LenThucDonTuan')
os.makedirs(APP_DATA, exist_ok=True)

# OpenAI API configuration
OPENAI_API_KEY = get_api_key()
OPENAI_MODEL = "gpt-4.1-mini-2025-04-14"  # Sử dụng model mới nhất và tốt nhất

# Database configuration
DATABASE_PATH = os.path.join(APP_DATA, 'data.db')

# UI configuration
APP_NAME = "Lên Thực Đơn Tuần"
APP_VERSION = "1.0.0"
DEFAULT_WINDOW_WIDTH = 1024
DEFAULT_WINDOW_HEIGHT = 768

# Cuisine types
CUISINE_TYPES = [
    "Ẩm thực miền Nam Việt Nam",
    "Ẩm thực miền Bắc Việt Nam",
    "Ẩm thực miền Trung Việt Nam",
    "Ẩm thực Pháp",
    "Ẩm thực Ý",
    "Ẩm thực Trung Hoa",
    "Ẩm thực Nhật Bản",
    "Ẩm thực Hàn Quốc",
    "Ẩm thực Thái Lan",
    "Ẩm thực Ấn Độ"
]

# Budget options (in VND)
BUDGET_OPTIONS = [
    "50000",
    "70000",
    "100000",
    "150000",
    "200000"
]

# Preparation time options (in minutes)
PREP_TIME_OPTIONS = [
    "30",
    "60",
    "90",
    "120",
    "180"
]

# Days of the week
DAYS_OF_WEEK = [
    "Thứ hai",
    "Thứ ba",
    "Thứ tư", 
    "Thứ năm",
    "Thứ sáu",
    "Thứ bảy",
    "Chủ nhật"
]

# Meals per day
MEALS_PER_DAY = [
    "Bữa sáng",
    "Bữa trưa",
    "Bữa tối"
] 