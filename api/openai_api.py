"""
OpenAI API wrapper for generating menu suggestions.
"""
import os
import json
import logging
import openai
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

class OpenAIWrapper:
    """Wrapper for OpenAI API."""
    
    def __init__(self, api_key=OPENAI_API_KEY, model=OPENAI_MODEL):
        """Initialize OpenAI client with API key."""
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key
    
    def _parse_json_response(self, content):
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
                        return json.loads(content)
                else:
                    logger.error("No valid JSON object found in response")
                    return {"error": "No valid JSON object found in response"}
            except Exception as e:
                logger.error(f"JSON parsing error after all cleaning attempts: {str(e)}")
                return {"error": "Invalid JSON format in response"}
    
    def generate_weekly_menu(self, user_preferences, cuisine_type, 
                             budget_per_meal, max_prep_time, days, meals_per_day,
                             previous_meals=None):
        """
        Generate a weekly menu based on user preferences.
        
        Args:
            user_preferences: User preferences object with favorite/disliked items
            cuisine_type: Type of cuisine (e.g., "Ẩm thực miền Nam Việt Nam")
            budget_per_meal: Budget per meal in VND
            max_prep_time: Maximum preparation time in minutes
            days: List of days to generate menu for
            meals_per_day: List of meals per day (e.g., ["Bữa sáng", "Bữa trưa", "Bữa tối"])
            previous_meals: Dictionary of previous meals to optimize ingredients
            
        Returns:
            Dictionary with generated menu
        """
        prompt = self._create_menu_prompt(
            user_preferences, cuisine_type, budget_per_meal, 
            max_prep_time, days, meals_per_day, previous_meals
        )
        
        try:
            logger.info(f"Sending request to OpenAI API with model: {self.model}")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một đầu bếp chuyên nghiệp, giúp tạo thực đơn hàng tuần dựa trên sở thích cá nhân, ngân sách và thời gian chuẩn bị. Phản hồi của bạn phải ở định dạng JSON theo mẫu được cung cấp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            # Log the raw response
            logger.info("Raw API Response Object:")
            logger.info(str(response))
            
            # Extract content and parse JSON
            content = response.choices[0].message['content']
            
            # Check if response was truncated
            if response.choices[0].finish_reason == "length":
                logger.warning("Response was truncated. Attempting to fix JSON.")
                # Try to find the last complete object
                last_brace = content.rfind('}')
                if last_brace != -1:
                    content = content[:last_brace + 1]
                    # Add missing closing braces if needed
                    open_braces = content.count('{')
                    close_braces = content.count('}')
                    if open_braces > close_braces:
                        content += '}' * (open_braces - close_braces)
            
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Error in generate_weekly_menu: {str(e)}")
            return {"error": str(e)}
    
    def _create_menu_prompt(self, user_preferences, cuisine_type, 
                           budget_per_meal, max_prep_time, days, 
                           meals_per_day, previous_meals=None):
        """Create a prompt for the OpenAI API to generate a menu."""
        
        # Base prompt with user preferences - optimized for token usage
        prompt = f"""Tạo thực đơn:
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
            prompt += "\nTối ưu từ:"
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
        "name": "tên",
        "ingredients": ["nguyên liệu"],
        "preparation_time": phút,
        "estimated_cost": đồng,
        "reused_ingredients": ["tái sử dụng"]
      }
    }
  },
  "optimization_notes": ["ghi chú"]
}"""
        
        return prompt
    
    def generate_recipe(self, dish_name, cuisine_type=None):
        """
        Generate a detailed recipe for a specific dish.
        
        Args:
            dish_name: Name of the dish
            cuisine_type: Type of cuisine (optional)
            
        Returns:
            Dictionary with recipe details
        """
        cuisine_str = f" theo phong cách {cuisine_type}" if cuisine_type else ""
        prompt = f"Hãy cung cấp công thức chi tiết để nấu món {dish_name}{cuisine_str} theo format JSON sau:\n"
        prompt += """{
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
    "preparation_time": "thời gian chuẩn bị (phút)",
    "cooking_time": "thời gian nấu (phút)",
    "servings": "số người ăn",
    "difficulty": "độ khó (dễ/trung bình/khó)"
  }
}"""
        
        try:
            logger.info(f"Sending recipe request to OpenAI API with model: {self.model}")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một đầu bếp chuyên nghiệp, cung cấp công thức nấu ăn chi tiết. Phản hồi của bạn phải ở định dạng JSON theo mẫu được cung cấp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            # Log the raw response
            logger.info("Raw API Response Object:")
            logger.info(str(response))
            
            # Extract content and parse JSON
            content = response.choices[0].message['content']
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Error in generate_recipe: {str(e)}")
            return {"error": str(e)} 