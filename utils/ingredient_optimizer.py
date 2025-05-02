"""
Utility for optimizing ingredient usage across meals.
"""
from collections import Counter


class IngredientOptimizer:
    """Utility class for optimizing ingredient usage."""
    
    @staticmethod
    def analyze_menu(menu):
        """
        Analyze a menu to find frequently used ingredients.
        
        Args:
            menu: Dictionary containing menu information
            
        Returns:
            Dictionary with ingredient usage analysis
        """
        ingredients = []
        days_with_meals = {}
        
        # Extract all ingredients from the menu
        for day, meals in menu.items():
            days_with_meals[day] = {}
            for meal_time, meal_info in meals.items():
                if 'ingredients' in meal_info:
                    days_with_meals[day][meal_time] = meal_info['name']
                    ingredients.extend(meal_info['ingredients'])
        
        # Count ingredient frequency
        ingredient_counter = Counter(ingredients)
        
        # Find most common ingredients
        most_common = ingredient_counter.most_common(10)
        
        return {
            'most_common_ingredients': most_common,
            'days_with_meals': days_with_meals,
            'total_unique_ingredients': len(ingredient_counter)
        }
    
    @staticmethod
    def find_reusable_ingredients(current_ingredients, previous_ingredients):
        """
        Find ingredients that can be reused from previous meals.
        
        Args:
            current_ingredients: List of ingredients for the current meal
            previous_ingredients: List of ingredients from previous meals
            
        Returns:
            List of ingredients that can be reused
        """
        return list(set(current_ingredients) & set(previous_ingredients))
    
    @staticmethod
    def suggest_optimizations(menu):
        """
        Suggest optimizations for ingredient usage across meals.
        
        Args:
            menu: Dictionary containing menu information
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Get all dishes and ingredients
        all_dishes = {}
        all_ingredients = []
        
        for day, meals in menu.items():
            for meal_time, meal_info in meals.items():
                dish_name = meal_info['name']
                ingredients = meal_info.get('ingredients', [])
                
                # Store dish info
                all_dishes[f"{day} - {meal_time}"] = {
                    'name': dish_name,
                    'ingredients': ingredients
                }
                
                # Add ingredients to the list
                all_ingredients.extend(ingredients)
        
        # Find common ingredients (used more than once)
        ingredient_counter = Counter(all_ingredients)
        common_ingredients = [item for item, count in ingredient_counter.items() if count > 1]
        
        # Generate suggestions for reusing ingredients
        for ingredient in common_ingredients:
            dishes_using_ingredient = []
            
            for dish_key, dish_info in all_dishes.items():
                if ingredient in dish_info['ingredients']:
                    dishes_using_ingredient.append(f"{dish_key} ({dish_info['name']})")
            
            if len(dishes_using_ingredient) > 1:
                suggestion = f"Nguyên liệu '{ingredient}' được sử dụng trong các món: {', '.join(dishes_using_ingredient)}"
                suggestions.append(suggestion)
        
        return suggestions
    
    @staticmethod
    def calculate_ingredient_usage(menu):
        """
        Calculate the overall usage of ingredients across the menu.
        
        Args:
            menu: Dictionary containing menu information
            
        Returns:
            Dictionary with ingredient usage statistics
        """
        ingredient_counter = Counter()
        
        # Count ingredients
        for day, meals in menu.items():
            for meal_time, meal_info in meals.items():
                ingredients = meal_info.get('ingredients', [])
                ingredient_counter.update(ingredients)
        
        # Calculate statistics
        total_ingredients = sum(ingredient_counter.values())
        unique_ingredients = len(ingredient_counter)
        
        # Calculate top ingredients
        top_ingredients = ingredient_counter.most_common(5)
        
        # Calculate usage efficiency (higher is better)
        usage_efficiency = total_ingredients / unique_ingredients if unique_ingredients > 0 else 0
        
        return {
            'total_ingredients': total_ingredients,
            'unique_ingredients': unique_ingredients,
            'top_ingredients': top_ingredients,
            'usage_efficiency': round(usage_efficiency, 2)
        } 