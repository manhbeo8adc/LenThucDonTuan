"""
Database models for the application.
"""
import sqlite3
import json
from datetime import datetime


class User:
    """User model representing user preferences."""
    
    def __init__(self, id=None, name=None, favorite_ingredients=None, 
                 disliked_ingredients=None, favorite_dishes=None, 
                 disliked_dishes=None):
        self.id = id
        self.name = name
        self.favorite_ingredients = favorite_ingredients or []
        self.disliked_ingredients = disliked_ingredients or []
        self.favorite_dishes = favorite_dishes or []
        self.disliked_dishes = disliked_dishes or []
    
    @classmethod
    def from_db_row(cls, row):
        """Create a User instance from a database row."""
        if not row:
            return None
        
        return cls(
            id=row[0],
            name=row[1],
            favorite_ingredients=json.loads(row[2]) if row[2] else [],
            disliked_ingredients=json.loads(row[3]) if row[3] else [],
            favorite_dishes=json.loads(row[4]) if row[4] else [],
            disliked_dishes=json.loads(row[5]) if row[5] else []
        )
    
    def to_dict(self):
        """Convert User to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'favorite_ingredients': self.favorite_ingredients,
            'disliked_ingredients': self.disliked_ingredients,
            'favorite_dishes': self.favorite_dishes,
            'disliked_dishes': self.disliked_dishes
        }


class Dish:
    """Dish model representing a meal."""
    
    def __init__(self, id=None, name=None, cuisine_type=None, 
                 ingredients=None, preparation_time=None, estimated_cost=None):
        self.id = id
        self.name = name
        self.cuisine_type = cuisine_type
        self.ingredients = ingredients or []
        self.preparation_time = preparation_time  # in minutes
        self.estimated_cost = estimated_cost  # in VND
    
    @classmethod
    def from_db_row(cls, row):
        """Create a Dish instance from a database row."""
        if not row:
            return None
        
        return cls(
            id=row[0],
            name=row[1],
            cuisine_type=row[2],
            ingredients=json.loads(row[3]) if row[3] else [],
            preparation_time=row[4],
            estimated_cost=row[5]
        )
    
    def to_dict(self):
        """Convert Dish to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'cuisine_type': self.cuisine_type,
            'ingredients': self.ingredients,
            'preparation_time': self.preparation_time,
            'estimated_cost': self.estimated_cost
        }


class Menu:
    """Menu model representing a weekly menu plan."""
    
    def __init__(self, id=None, user_id=None, name=None, creation_date=None,
                 cuisine_type=None, budget_per_meal=None, max_prep_time=None,
                 meals=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.creation_date = creation_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cuisine_type = cuisine_type
        self.budget_per_meal = budget_per_meal
        self.max_prep_time = max_prep_time
        self.meals = meals or {}  # Format: {day: {meal_time: dish_id}}
    
    @classmethod
    def from_db_row(cls, row):
        """Create a Menu instance from a database row."""
        if not row:
            return None
        
        return cls(
            id=row[0],
            user_id=row[1],
            name=row[2],
            creation_date=row[3],
            cuisine_type=row[4],
            budget_per_meal=row[5],
            max_prep_time=row[6],
            meals=json.loads(row[7]) if row[7] else {}
        )
    
    def to_dict(self):
        """Convert Menu to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'creation_date': self.creation_date,
            'cuisine_type': self.cuisine_type,
            'budget_per_meal': self.budget_per_meal,
            'max_prep_time': self.max_prep_time,
            'meals': self.meals
        } 