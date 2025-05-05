"""
OpenAI API wrapper for generating menu suggestions.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import openai
from PyQt5.QtCore import QObject, pyqtSignal
from config import OPENAI_MODEL
from utils.api_key_manager import get_api_key

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OpenAIWrapper(QObject):
    """Wrapper for OpenAI API."""
    
    # Signal to notify progress
    progress_signal = pyqtSignal(str)
    
    def __init__(self, model=OPENAI_MODEL):
        """Initialize OpenAI client with API key."""
        super().__init__()
        self.model = model
        self.api_key = get_api_key()
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        openai.api_key = self.api_key
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse and validate JSON response."""
        logger.info("Raw API Response:")
        logger.info(content)
        
        try:
            # First try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Direct JSON parsing failed, attempting to clean response")
            
            try:
                # Clean the response
                content = content.strip()
                
                # Remove any markdown code block markers
                content = content.replace('```json', '').replace('```', '')
                
                # Find the first { and last }
                start = content.find('{')
                end = content.rfind('}')
                
                if start != -1 and end != -1:
                    content = content[start:end + 1]
                    
                    # Replace any potential Unicode quotes with standard quotes
                    content = content.replace('"', '"').replace('"', '"')
                    content = content.replace(''', "'").replace(''', "'")
                    
                    # Remove any potential control characters
                    content = ''.join(char for char in content if ord(char) >= 32)
                    
                    logger.info("Cleaned JSON content:")
                    logger.info(content)
                    
                    try:
                        return json.loads(content)
                    except json.JSONDecoder as je:
                        logger.error(f"Failed to parse cleaned JSON: {str(je)}")
                        return None
            except Exception as e:
                logger.error(f"Error cleaning JSON: {str(e)}")
                return None
    
    def _create_menu_prompt(self, user_preferences, cuisine_type, 
                           budget_per_meal, max_prep_time, days, 
                           meals_per_day, servings=4, previous_meals=None):
        """Create a prompt for the OpenAI API to generate a menu."""
        
        # Base prompt with user preferences - optimized for token usage
        prompt = f"""Bạn là một đầu bếp chuyên nghiệp với kiến thức sâu rộng về ẩm thực {cuisine_type}. 
Hãy tạo một thực đơn hàng tuần phù hợp với văn hóa ẩm thực đã chọn, đảm bảo các yêu cầu sau:

1. Tất cả các món ăn PHẢI là những món ăn thực tế, phổ biến và tồn tại trong nền ẩm thực {cuisine_type}
2. KHÔNG được tạo ra hoặc kết hợp các món ăn không tồn tại trong thực tế
3. Mỗi ngày phải có thực đơn khác nhau, không lặp lại món ăn trong tuần
4. Các món ăn phải cân bằng dinh dưỡng (đạm, tinh bột, chất béo, vitamin)
5. Kết hợp nhiều phương pháp chế biến phù hợp với văn hóa ẩm thực đã chọn
6. Sử dụng nguyên liệu phổ biến, dễ tìm tại Việt Nam
7. Đảm bảo chi phí và thời gian nấu nướng nằm trong giới hạn cho phép
8. Trước khi đề xuất món ăn, hãy kiểm tra xem món đó có thực sự tồn tại và phổ biến trong nền ẩm thực đã chọn không

Thông tin chi tiết:
Ngày: {', '.join(days)}
Bữa: {', '.join(meals_per_day)}
Số người ăn: {servings} người
Thích: {', '.join(user_preferences.favorite_ingredients) if user_preferences.favorite_ingredients else 'Không'}
Không thích: {', '.join(user_preferences.disliked_ingredients) if user_preferences.disliked_ingredients else 'Không'}
Món thích: {', '.join(user_preferences.favorite_dishes) if user_preferences.favorite_dishes else 'Không'}
Món không thích: {', '.join(user_preferences.disliked_dishes) if user_preferences.disliked_dishes else 'Không'}
Phong cách: {cuisine_type}
Ngân sách/bữa: {budget_per_meal}đ
Thời gian max: {max_prep_time}p"""
        
        # Add optimization instruction if needed
        if previous_meals:
            prompt += "\n\nTối ưu từ thực đơn trước:"
            for day, meals in previous_meals.items():
                for meal_time, meal_info in meals.items():
                    prompt += f"\n{day}-{meal_time}: {meal_info['name']} ({', '.join(meal_info['ingredients'])})"
        
        # Format instructions - simplified
        prompt += """
Format JSON:
{
  "menu": {
    "Ngày": {
      "Bữa": {
        "name": "tên món (phải là món ăn thực tế, phổ biến)",
        "ingredients": ["nguyên liệu phổ biến, dễ tìm"],
        "preparation_time": phút,
        "estimated_cost": đồng,
        "servings": số người,
        "reused_ingredients": ["tái sử dụng"],
        "nutrition_info": {
          "protein": "g",
          "carbs": "g",
          "fat": "g",
          "calories": "kcal"
        },
        "cooking_method": "phương pháp nấu phù hợp với văn hóa ẩm thực",
        "food_groups": ["nhóm thực phẩm"]
      }
    }
  },
  "optimization_notes": ["ghi chú về tối ưu nguyên liệu"]
}"""
        
        # Log the prompt
        logger.info("Generated prompt:")
        logger.info(prompt)
        
        return prompt
    
    def _generate_daily_menu(self, user_preferences, cuisine_type,
                           budget_per_meal, max_prep_time, day,
                           meals_per_day, servings, previous_meals=None, 
                           generated_dishes=None) -> Dict[str, Any]:
        """Generate menu for a single day."""
        if generated_dishes is None:
            generated_dishes = []
        
        prompt = f"""Với vai trò là một đầu bếp chuyên về {cuisine_type}, hãy tạo thực đơn cho {day} với các yêu cầu sau:

1. Tất cả các món ăn PHẢI là những món ăn thực tế, phổ biến và tồn tại trong nền ẩm thực {cuisine_type}
2. KHÔNG được tạo ra hoặc kết hợp các món ăn không tồn tại trong thực tế
3. Sử dụng nguyên liệu phổ biến, dễ tìm tại Việt Nam
4. Đảm bảo chi phí và thời gian nấu nướng nằm trong giới hạn
5. Trước khi đề xuất món ăn, hãy kiểm tra xem món đó có thực sự tồn tại và phổ biến trong nền ẩm thực đã chọn không

Thông tin chi tiết:
Các bữa: {', '.join(meals_per_day)}
Số người ăn: {servings} người
Thích: {', '.join(user_preferences.favorite_ingredients) if user_preferences.favorite_ingredients else 'Không'}
Không thích: {', '.join(user_preferences.disliked_ingredients) if user_preferences.disliked_ingredients else 'Không'}
Món thích: {', '.join(user_preferences.favorite_dishes) if user_preferences.favorite_dishes else 'Không'}
Món không thích: {', '.join(user_preferences.disliked_dishes) if user_preferences.disliked_dishes else 'Không'}
Phong cách: {cuisine_type}
Ngân sách/bữa: {budget_per_meal}đ
Thời gian tối đa: {max_prep_time}p

Không sử dụng các món đã có trước đây: {', '.join(generated_dishes) if generated_dishes else 'Không'}

Format JSON:
{{
  "{day}": {{
"""
        # Add format for each meal
        for meal in meals_per_day:
            prompt += f"""    "{meal}": {{
      "name": "tên món (phải là món ăn thực tế, phổ biến)",
      "ingredients": ["nguyên liệu phổ biến, dễ tìm"],
      "preparation_time": phút,
      "estimated_cost": đồng,
      "servings": {servings},
      "reused_ingredients": ["tái sử dụng"],
      "nutrition_info": {{
        "protein": "g",
        "carbs": "g",
        "fat": "g",
        "calories": "kcal"
      }},
      "cooking_method": "phương pháp nấu phù hợp với văn hóa ẩm thực",
      "food_groups": ["nhóm thực phẩm"]
    }},
"""
        
        # Close the JSON structure
        prompt = prompt.rstrip(",\n") + "\n  }\n}"
        
        try:
            # Call API to generate the daily menu
            response = self.generate_menu(prompt)
            
            # Parse and extract new dish names for tracking
            if response and day in response:
                for meal_time, meal_info in response[day].items():
                    if isinstance(meal_info, dict) and "name" in meal_info:
                        generated_dishes.append(meal_info["name"])
            
            return response
        except Exception as e:
            logger.error(f"Error generating daily menu: {str(e)}")
            return {"error": f"Lỗi khi tạo thực đơn cho {day}: {str(e)}"}
    
    def generate_recipe(self, dish_name: str, cuisine_type: Optional[str] = None, servings: int = 4) -> Dict[str, Any]:
        """Generate a detailed recipe for a specific dish."""
        # Emit progress signal
        self.progress_signal.emit(f"Đang tạo công thức cho món {dish_name}...")
        
        cuisine_str = f" theo phong cách {cuisine_type}" if cuisine_type else ""
        
        # Create prompt with proper formatting
        prompt = f"""Với vai trò là một đầu bếp chuyên về {cuisine_type}, hãy cung cấp công thức chi tiết cho món {dish_name} cho {servings} người.

Yêu cầu:
1. Đảm bảo đây là một món ăn thực tế, phổ biến trong nền ẩm thực {cuisine_type}
2. Sử dụng nguyên liệu phổ biến, dễ tìm tại Việt Nam
3. Hướng dẫn chi tiết các bước thực hiện
4. Tất cả các giá trị số (thời gian, khối lượng) phải là số nguyên
5. Đảm bảo định lượng nguyên liệu phù hợp cho {servings} người ăn

Format JSON:
{{
  "recipe": {{
    "name": "tên món ăn",
    "cuisine_type": "{cuisine_type}",
    "ingredients": [
      {{
        "item": "tên nguyên liệu",
        "amount": số lượng,
        "unit": "đơn vị"
      }}
    ],
    "steps": [
      {{
        "step": 1,
        "description": "mô tả chi tiết cách thực hiện"
      }}
    ],
    "preparation_time": thời gian chuẩn bị (phút),
    "cooking_time": thời gian nấu (phút),
    "servings": {servings},
    "difficulty": "độ khó (dễ/trung bình/khó)"
  }}
}}"""
        
        try:
            logger.info(f"Sending recipe request to OpenAI API with model: {self.model}")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Bạn là một đầu bếp chuyên nghiệp về ẩm thực {cuisine_type}, cung cấp công thức nấu ăn chi tiết và chính xác. Phản hồi của bạn phải ở định dạng JSON theo mẫu được cung cấp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}  # Force JSON response format
            )
            
            # Log the raw response
            logger.info("Raw API Response Object:")
            logger.info(str(response))
            
            # Extract content and parse JSON
            content = response.choices[0].message['content']
            result = self._parse_json_response(content)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating recipe: {str(e)}")
            return None
    
    def _refresh_api_key(self):
        """Refresh API key from manager."""
        self.api_key = get_api_key()
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_menu(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate menu using OpenAI API."""
        try:
            logger.info("Sending request to OpenAI API")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một đầu bếp chuyên nghiệp với kiến thức sâu rộng về ẩm thực. Hãy đảm bảo chỉ đề xuất những món ăn thực tế, phổ biến và phù hợp với văn hóa ẩm thực được chọn."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}  # Force JSON response format
            )
            
            logger.info("Raw API Response:")
            logger.info(response)
            
            # Extract the generated menu from the response
            menu_text = response.choices[0].message.content
            try:
                menu_data = json.loads(menu_text)
                return menu_data
            except json.JSONDecodeError:
                logger.error("Failed to parse menu JSON")
                return None
                
        except openai.error.AuthenticationError:
            # Try refreshing the API key
            self._refresh_api_key()
            if not self.api_key:
                logger.error("Authentication failed and could not refresh API key")
                return None
            # Retry with new API key
            return self.generate_menu(prompt)
            
        except Exception as e:
            logger.error(f"Error generating menu: {str(e)}")
            return None
    
    def get_recipe(self, dish_name: str, cuisine_type: str) -> Optional[Dict[str, Any]]:
        """Get detailed recipe for a dish."""
        try:
            prompt = f"""
            Please provide a detailed recipe for "{dish_name}" in {cuisine_type} style.
            Include:
            - List of ingredients with quantities
            - Step by step cooking instructions
            - Preparation time
            - Cooking time
            - Number of servings
            - Difficulty level
            
            Format the response as a JSON object.
            """
            
            logger.info("Sending recipe request to OpenAI API with model: %s", self.model)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional chef providing detailed recipes."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            logger.info("Raw API Response Object:")
            logger.info(response)
            
            recipe_text = response.choices[0].message.content
            logger.info("Raw API Response:")
            logger.info(recipe_text)
            
            try:
                recipe_data = json.loads(recipe_text)
                logger.info("Recipe data: %s", recipe_data)
                return recipe_data
            except json.JSONDecodeError:
                logger.error("Failed to parse recipe JSON")
                return None
                
        except openai.error.AuthenticationError:
            # Try refreshing the API key
            self._refresh_api_key()
            if not self.api_key:
                logger.error("Authentication failed and could not refresh API key")
                return None
            # Retry with new API key
            return self.get_recipe(dish_name, cuisine_type)
            
        except Exception as e:
            logger.error(f"Error getting recipe: {str(e)}")
            return None
    
    def generate_weekly_menu(self, user_preferences, cuisine_type, 
                              budget_per_meal, max_prep_time, days, meals_per_day,
                              servings=4, previous_meals=None) -> Dict[str, Any]:
        """Generate a weekly menu based on user preferences."""
        try:
            self.progress_signal.emit("Bắt đầu tạo thực đơn tuần...")
            menu = {"menu": {}}
            generated_dishes = []
            for day in days:
                self.progress_signal.emit(f"Đang tạo thực đơn cho {day}...")
                day_menu = self._generate_daily_menu(
                    user_preferences, cuisine_type, budget_per_meal,
                    max_prep_time, day, meals_per_day, servings, previous_meals,
                    generated_dishes
                )
                if "error" in day_menu:
                    return day_menu
                menu["menu"][day] = day_menu.get(day, {})
                for meal_time, meal_info in menu["menu"][day].items():
                    if isinstance(meal_info, dict) and "name" in meal_info:
                        generated_dishes.append(meal_info["name"])
            self.progress_signal.emit("Đã hoàn thành tạo thực đơn tuần!")
            return menu
        except Exception as e:
            logger.error(f"Error in generate_weekly_menu: {str(e)}")
            return {"error": str(e)} 