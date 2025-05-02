"""
Helper utility functions for the application.
"""
import json
import os
from datetime import datetime


def format_currency(amount):
    """
    Format a number as currency in VND.
    
    Args:
        amount: The amount to format
        
    Returns:
        Formatted currency string
    """
    return f"{amount:,} VND".replace(",", ".")


def format_time(minutes):
    """
    Format minutes as a readable time string.
    
    Args:
        minutes: Number of minutes
        
    Returns:
        Formatted time string
    """
    if minutes < 60:
        return f"{minutes} phút"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours} giờ"
    
    return f"{hours} giờ {remaining_minutes} phút"


def save_json(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Target filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON: {str(e)}")
        return False


def load_json(filename):
    """
    Load data from a JSON file.
    
    Args:
        filename: Source filename
        
    Returns:
        Loaded data or None if file doesn't exist
    """
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {str(e)}")
        return None


def get_current_datetime():
    """
    Get the current datetime formatted as a string.
    
    Returns:
        Formatted datetime string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_unique_filename(prefix, extension="json"):
    """
    Generate a unique filename with a timestamp.
    
    Args:
        prefix: Prefix for the filename
        extension: File extension (default: json)
        
    Returns:
        Unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def ensure_directory_exists(directory):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except Exception as e:
            print(f"Error creating directory: {str(e)}")
            return False
    return True


def export_menu_to_text(menu, filename):
    """
    Export a menu to a text file.
    
    Args:
        menu: Menu dictionary
        filename: Target filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("THỰC ĐƠN TUẦN\n\n")
            
            for day, meals in menu.items():
                if day == "optimization_notes":
                    continue
                    
                f.write(f"=== {day} ===\n")
                
                for meal_time, meal_info in meals.items():
                    f.write(f"\n{meal_time}: {meal_info['name']}\n")
                    f.write(f"Nguyên liệu: {', '.join(meal_info['ingredients'])}\n")
                    f.write(f"Thời gian chuẩn bị: {format_time(meal_info['preparation_time'])}\n")
                    f.write(f"Chi phí ước tính: {format_currency(meal_info['estimated_cost'])}\n")
                    
                    if 'reused_ingredients' in meal_info and meal_info['reused_ingredients']:
                        f.write(f"Nguyên liệu tái sử dụng: {', '.join(meal_info['reused_ingredients'])}\n")
                
                f.write("\n" + "-" * 50 + "\n")
            
            # Add optimization notes if available
            if 'optimization_notes' in menu:
                f.write("\nGHI CHÚ TỐI ƯU HÓA NGUYÊN LIỆU:\n")
                for note in menu['optimization_notes']:
                    f.write(f"- {note}\n")
        
        return True
    except Exception as e:
        print(f"Error exporting menu: {str(e)}")
        return False 