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
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.log')
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
                    except json.JSONDecodeError as je:
                        logger.error(f"JSON parsing error after cleaning: {str(je)}")
                        # Try to fix common JSON formatting issues
                        content = content.replace("'", '"')  # Replace single quotes with double quotes
                        content = content.replace(",}", "}")  # Remove trailing commas
                        content = content.replace(",]", "]")  # Remove trailing commas in arrays
                        
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            # Additional fallback - create a minimal valid structure
                            logger.error("All JSON parsing attempts failed. Creating fallback structure.")
                            if "recipe" in content.lower():
                                return {
                                    "recipe": {
                                        "name": "Unknown recipe",
                                        "ingredients": ["Could not parse ingredients"],
                                        "steps": ["Could not parse preparation steps"],
                                        "error": "Invalid JSON format in original response"
                                    }
                                }
                            else:
                                return {"error": "Invalid JSON format in response"}
                else:
                    logger.error("No valid JSON object found in response")
                    return {"error": "No valid JSON object found in response"}
            except Exception as e:
                logger.error(f"JSON parsing error after all cleaning attempts: {str(e)}")
                return {"error": "Invalid JSON format in response"}
    
    def _create_menu_prompt(self, user_preferences, cuisine_type, 
                           budget_per_meal, max_prep_time, days, 
                           meals_per_day, servings=4, previous_meals=None):
        """Create a prompt for the OpenAI API to generate a menu."""
        
        # Base prompt with user preferences - optimized for token usage
        prompt = f"""Bạn là một đầu bếp chuyên nghiệp với kiến thức sâu rộng về dinh dưỡng và ẩm thực. 
Hãy tạo một thực đơn hàng tuần đa dạng, hấp dẫn và đầy đủ chất dinh dưỡng với các yêu cầu sau:

1. Mỗi ngày phải có thực đơn khác nhau, không lặp lại món ăn trong tuần
2. Các món ăn phải cân bằng dinh dưỡng (đạm, tinh bột, chất béo, vitamin)
3. Kết hợp nhiều phương pháp chế biến (xào, hấp, luộc, nướng, chiên)
4. Sử dụng nguyên liệu tươi, theo mùa
5. Đảm bảo mỗi bữa có đủ 4 nhóm thực phẩm chính
6. Các món ăn phải hấp dẫn, ngon miệng và dễ ăn

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
        "name": "tên món",
        "ingredients": ["nguyên liệu"],
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
        "cooking_method": "phương pháp nấu",
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

    def generate_weekly_menu(self, user_preferences, cuisine_type, 
                             budget_per_meal, max_prep_time, days, meals_per_day,
                             servings=4, previous_meals=None) -> Dict[str, Any]:
        """Generate a weekly menu based on user preferences."""
        try:
            # Initial progress notification
            self.progress_signal.emit("Bắt đầu tạo thực đơn tuần...")
            
            # Generate menu day by day
            menu = {"menu": {}}
            
            # Keep track of dishes already generated to avoid repetition
            generated_dishes = []
            
            # Map day numbers to Vietnamese names for display
            day_names = {
                "Thứ hai": "Thứ Hai", 
                "Thứ ba": "Thứ Ba", 
                "Thứ tư": "Thứ Tư",
                "Thứ năm": "Thứ Năm", 
                "Thứ sáu": "Thứ Sáu", 
                "Thứ bảy": "Thứ Bảy",
                "Chủ nhật": "Chủ Nhật"
            }
            
            for day in days:
                # Emit detailed progress signal with proper formatting
                display_day = day_names.get(day, day)
                self.progress_signal.emit(f"Đang tạo thực đơn cho {display_day}...")
                
                logger.info(f"Generating menu for {day}")
                day_menu = self._generate_daily_menu(
                    user_preferences, cuisine_type, budget_per_meal,
                    max_prep_time, day, meals_per_day, servings, previous_meals,
                    generated_dishes
                )
                if "error" in day_menu:
                    return day_menu
                
                # Handle both array and object responses
                if isinstance(day_menu.get(day, {}).get("Bữa"), list):
                    # Convert array format to object format
                    meals_dict = {}
                    for meal in day_menu[day]["Bữa"]:
                        meal_name = meal["name"].split(" - ")[0].strip()  # Extract meal time
                        meals_dict[meal_name] = meal
                    menu["menu"][day] = meals_dict
                else:
                    menu["menu"][day] = day_menu.get(day, {})
                
                # Add this day's dishes to the list of generated dishes
                for meal_time, meal_info in menu["menu"][day].items():
                    generated_dishes.append(meal_info["name"])
            
            # Signal completion
            self.progress_signal.emit("Đã hoàn thành tạo thực đơn tuần!")
            return menu
            
        except Exception as e:
            logger.error(f"Error in generate_weekly_menu: {str(e)}")
            return {"error": str(e)}
    
    def _generate_daily_menu(self, user_preferences, cuisine_type,
                           budget_per_meal, max_prep_time, day,
                           meals_per_day, servings, previous_meals=None, 
                           generated_dishes=None) -> Dict[str, Any]:
        """Generate menu for a single day."""
        if generated_dishes is None:
            generated_dishes = []
        
        prompt = f"""Tạo một thực đơn cho {day} với các bữa: {', '.join(meals_per_day)}.
Mỗi món ăn phải cân bằng dinh dưỡng và phù hợp với yêu cầu thực đơn tuần.

Thông tin chi tiết:
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
      "name": "tên món",
      "ingredients": ["nguyên liệu 1", "nguyên liệu 2"],
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
      "cooking_method": "phương pháp nấu",
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
        prompt = f"Hãy cung cấp công thức chi tiết để nấu món {dish_name}{cuisine_str} cho {servings} người theo format JSON sau.\n"
        prompt += "Chú ý: Đảm bảo rằng tất cả các giá trị số (thời gian, khẩu phần) phải là số nguyên, không phải chuỗi.\n\n"
        prompt += f"""
{{
  "recipe": {{
    "name": "tên món ăn",
    "cuisine_type": "loại ẩm thực",
    "ingredients": [
      {{
        "item": "tên nguyên liệu",
        "amount": "số lượng",
        "unit": "đơn vị"
      }}
    ],
    "steps": [
      {{
        "step": 1,
        "description": "mô tả bước thực hiện"
      }}
    ],
    "preparation_time": 30,
    "cooking_time": 45,
    "servings": {servings},
    "difficulty": "độ khó (dễ/trung bình/khó)"
  }}
}}

Lưu ý quan trọng: 
1. Bạn PHẢI trả về JSON hợp lệ
2. Tất cả các giá trị số như preparation_time, cooking_time, servings, và step phải là số nguyên, KHÔNG phải chuỗi
3. Đảm bảo đúng định dạng và không có lỗi cú pháp JSON
4. Nguyên liệu phải được tính toán chính xác cho {servings} người ăn
"""
        
        try:
            logger.info(f"Sending recipe request to OpenAI API with model: {self.model}")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một đầu bếp chuyên nghiệp, cung cấp công thức nấu ăn chi tiết. Phản hồi của bạn phải ở định dạng JSON theo mẫu được cung cấp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"}  # Force JSON response format
            )
            
            # Log the raw response
            logger.info("Raw API Response Object:")
            logger.info(str(response))
            
            # Extract content and parse JSON
            content = response.choices[0].message['content']
            result = self._parse_json_response(content)
            
            # Validate and fix numeric values
            if "recipe" in result:
                recipe = result["recipe"]
                # Convert preparation_time to int
                if "preparation_time" in recipe:
                    try:
                        recipe["preparation_time"] = int(recipe["preparation_time"])
                    except (ValueError, TypeError):
                        recipe["preparation_time"] = 30
                
                # Convert cooking_time to int
                if "cooking_time" in recipe:
                    try:
                        recipe["cooking_time"] = int(recipe["cooking_time"])
                    except (ValueError, TypeError):
                        recipe["cooking_time"] = 45
                
                # Convert servings to int
                if "servings" in recipe:
                    try:
                        recipe["servings"] = int(recipe["servings"])
                    except (ValueError, TypeError):
                        recipe["servings"] = 2
                
                # Ensure steps have integer step numbers
                if "steps" in recipe and isinstance(recipe["steps"], list):
                    for i, step in enumerate(recipe["steps"]):
                        if isinstance(step, dict) and "step" in step:
                            try:
                                step["step"] = int(step["step"])
                            except (ValueError, TypeError):
                                step["step"] = i + 1
            
            # Signal completion
            self.progress_signal.emit(f"Đã hoàn thành tạo công thức cho món {dish_name}!")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_recipe: {str(e)}")
            return {"error": str(e)}

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
                    {"role": "system", "content": "You are a professional chef with extensive knowledge of nutrition and cuisine."},
                    {"role": "user", "content": prompt}
                ]
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