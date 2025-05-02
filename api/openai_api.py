"""
OpenAI API wrapper for generating menu suggestions.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import openai
from PyQt5.QtCore import QObject, pyqtSignal
from config import OPENAI_API_KEY, OPENAI_MODEL

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
    
    def __init__(self, api_key=OPENAI_API_KEY, model=OPENAI_MODEL):
        """Initialize OpenAI client with API key."""
        super().__init__()
        self.api_key = api_key
        self.model = model
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
                           meals_per_day, previous_meals=None):
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
                             previous_meals=None) -> Dict[str, Any]:
        """Generate a weekly menu based on user preferences."""
        try:
            # Generate menu day by day
            menu = {"menu": {}}
            
            # Keep track of dishes already generated to avoid repetition
            generated_dishes = []
            
            for day in days:
                # Emit progress signal
                self.progress_signal.emit(f"Đang tạo thực đơn cho {day}...")
                
                logger.info(f"Generating menu for {day}")
                day_menu = self._generate_daily_menu(
                    user_preferences, cuisine_type, budget_per_meal,
                    max_prep_time, day, meals_per_day, previous_meals,
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
            self.progress_signal.emit("Đã hoàn thành tạo thực đơn!")
            return menu
            
        except Exception as e:
            logger.error(f"Error in generate_weekly_menu: {str(e)}")
            return {"error": str(e)}
    
    def _generate_daily_menu(self, user_preferences, cuisine_type,
                           budget_per_meal, max_prep_time, day,
                           meals_per_day, previous_meals=None, 
                           generated_dishes=None) -> Dict[str, Any]:
        """Generate menu for a single day."""
        # Initialize generated_dishes if None
        if generated_dishes is None:
            generated_dishes = []
        
        prompt = f"""Bạn là một đầu bếp chuyên nghiệp với kiến thức sâu rộng về dinh dưỡng và ẩm thực. 
Hãy tạo thực đơn cho {day} với các yêu cầu sau:

1. Thực đơn phải khác biệt với các ngày khác trong tuần
2. Các món ăn phải cân bằng dinh dưỡng (đạm, tinh bột, chất béo, vitamin)
3. Kết hợp nhiều phương pháp chế biến (xào, hấp, luộc, nướng, chiên)
4. Sử dụng nguyên liệu tươi, theo mùa
5. Đảm bảo mỗi bữa có đủ 4 nhóm thực phẩm chính
6. Các món ăn phải hấp dẫn, ngon miệng và dễ ăn
7. KHÔNG ĐƯỢC lặp lại những món ăn đã có trong thực đơn các ngày trước

Thông tin chi tiết:
Bữa: {', '.join(meals_per_day)}
Thích: {', '.join(user_preferences.favorite_ingredients) if user_preferences.favorite_ingredients else 'Không'}
Không thích: {', '.join(user_preferences.disliked_ingredients) if user_preferences.disliked_ingredients else 'Không'}
Món thích: {', '.join(user_preferences.favorite_dishes) if user_preferences.favorite_dishes else 'Không'}
Món không thích: {', '.join(user_preferences.disliked_dishes) if user_preferences.disliked_dishes else 'Không'}
Phong cách: {cuisine_type}
Ngân sách/bữa: {budget_per_meal}đ
Thời gian max: {max_prep_time}p"""

        # Add previously generated dishes to avoid repetition
        if generated_dishes:
            prompt += "\n\nCác món ăn đã có trong thực đơn trước đó (KHÔNG ĐƯỢC lặp lại):"
            for i, dish in enumerate(generated_dishes, 1):
                prompt += f"\n{i}. {dish}"

        # Add optimization instruction if needed
        if previous_meals:
            prompt += "\n\nTối ưu từ thực đơn trước:"
            for day, meals in previous_meals.items():
                for meal_time, meal_info in meals.items():
                    prompt += f"\n{day}-{meal_time}: {meal_info['name']} ({', '.join(meal_info['ingredients'])})"
        
        # Format instructions - simplified
        prompt += f"""
Format JSON:
{{
  "{day}": {{
    "Bữa sáng": {{
      "name": "tên món",
      "ingredients": ["nguyên liệu"],
      "preparation_time": phút,
      "estimated_cost": đồng,
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
    "Bữa trưa": {{
      // tương tự như bữa sáng
    }},
    "Bữa tối": {{
      // tương tự như bữa sáng
    }}
  }}
}}"""

        # Log the prompt
        logger.info(f"Generated prompt for {day}:")
        logger.info(prompt)

        try:
            logger.info(f"Sending request to OpenAI API for {day}")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một đầu bếp chuyên nghiệp, giúp tạo thực đơn cho một ngày dựa trên sở thích cá nhân, ngân sách và thời gian chuẩn bị. Phản hồi của bạn phải ở định dạng JSON theo mẫu được cung cấp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Increased for more creativity
                max_tokens=800
            )
            
            # Log the raw response
            logger.info(f"Raw API Response for {day}:")
            logger.info(str(response))
            
            # Extract content and parse JSON
            content = response.choices[0].message['content']
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Error generating menu for {day}: {str(e)}")
            return {"error": f"Error generating menu for {day}: {str(e)}"}
    
    def generate_recipe(self, dish_name: str, cuisine_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate a detailed recipe for a specific dish."""
        # Emit progress signal
        self.progress_signal.emit(f"Đang tạo công thức cho món {dish_name}...")
        
        cuisine_str = f" theo phong cách {cuisine_type}" if cuisine_type else ""
        
        # Create prompt with proper formatting
        prompt = f"Hãy cung cấp công thức chi tiết để nấu món {dish_name}{cuisine_str} theo format JSON sau.\n"
        prompt += "Chú ý: Đảm bảo rằng tất cả các giá trị số (thời gian, khẩu phần) phải là số nguyên, không phải chuỗi.\n\n"
        prompt += """
{
  "recipe": {
    "name": "tên món ăn",
    "cuisine_type": "loại ẩm thực",
    "ingredients": [
      {
        "item": "tên nguyên liệu",
        "amount": "số lượng",
        "unit": "đơn vị"
      }
    ],
    "steps": [
      {
        "step": 1,
        "description": "mô tả bước thực hiện"
      }
    ],
    "preparation_time": 30,
    "cooking_time": 45,
    "servings": 4,
    "difficulty": "độ khó (dễ/trung bình/khó)"
  }
}

Lưu ý quan trọng: 
1. Bạn PHẢI trả về JSON hợp lệ
2. Tất cả các giá trị số như preparation_time, cooking_time, servings, và step phải là số nguyên, KHÔNG phải chuỗi
3. Đảm bảo đúng định dạng và không có lỗi cú pháp JSON
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