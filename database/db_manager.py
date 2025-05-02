"""
Database manager for handling database operations.
"""
import sqlite3
import json
import os
from .models import User, Dish, Menu, Recipe
from config import DATABASE_PATH


class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, db_path=DATABASE_PATH):
        """Initialize the database manager with the database path."""
        self.db_path = db_path
        self._create_tables_if_not_exist()
    
    def _get_connection(self):
        """Get a connection to the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables_if_not_exist(self):
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            favorite_ingredients TEXT,
            disliked_ingredients TEXT,
            favorite_dishes TEXT,
            disliked_dishes TEXT
        )
        ''')
        
        # Create Dishes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine_type TEXT,
            ingredients TEXT,
            preparation_time INTEGER,
            estimated_cost INTEGER
        )
        ''')
        
        # Create Menus table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            creation_date TEXT,
            cuisine_type TEXT,
            budget_per_meal INTEGER,
            max_prep_time INTEGER,
            meals TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create Recipes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine_type TEXT,
            content TEXT,
            creation_date TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # User operations
    def save_user(self, user):
        """Save a user to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if user.id is None:
            # Insert new user
            cursor.execute('''
            INSERT INTO users (name, favorite_ingredients, disliked_ingredients, 
                              favorite_dishes, disliked_dishes)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                user.name,
                json.dumps(user.favorite_ingredients),
                json.dumps(user.disliked_ingredients),
                json.dumps(user.favorite_dishes),
                json.dumps(user.disliked_dishes)
            ))
            user.id = cursor.lastrowid
        else:
            # Update existing user
            cursor.execute('''
            UPDATE users
            SET name = ?, favorite_ingredients = ?, disliked_ingredients = ?,
                favorite_dishes = ?, disliked_dishes = ?
            WHERE id = ?
            ''', (
                user.name,
                json.dumps(user.favorite_ingredients),
                json.dumps(user.disliked_ingredients),
                json.dumps(user.favorite_dishes),
                json.dumps(user.disliked_dishes),
                user.id
            ))
        
        conn.commit()
        conn.close()
        return user
    
    def get_user(self, user_id):
        """Get a user by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return User.from_db_row(tuple(row))
        return None
    
    def get_all_users(self):
        """Get all users."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [User.from_db_row(tuple(row)) for row in rows]
    
    def delete_user(self, user_id):
        """Delete a user by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    # Dish operations
    def save_dish(self, dish):
        """Save a dish to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if dish.id is None:
            # Insert new dish
            cursor.execute('''
            INSERT INTO dishes (name, cuisine_type, ingredients, preparation_time, estimated_cost)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                dish.name,
                dish.cuisine_type,
                json.dumps(dish.ingredients),
                dish.preparation_time,
                dish.estimated_cost
            ))
            dish.id = cursor.lastrowid
        else:
            # Update existing dish
            cursor.execute('''
            UPDATE dishes
            SET name = ?, cuisine_type = ?, ingredients = ?, 
                preparation_time = ?, estimated_cost = ?
            WHERE id = ?
            ''', (
                dish.name,
                dish.cuisine_type,
                json.dumps(dish.ingredients),
                dish.preparation_time,
                dish.estimated_cost,
                dish.id
            ))
        
        conn.commit()
        conn.close()
        return dish
    
    def get_dish(self, dish_id):
        """Get a dish by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return Dish.from_db_row(tuple(row))
        return None
    
    def get_all_dishes(self, cuisine_type=None):
        """Get all dishes, optionally filtered by cuisine type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if cuisine_type:
            cursor.execute('SELECT * FROM dishes WHERE cuisine_type = ?', (cuisine_type,))
        else:
            cursor.execute('SELECT * FROM dishes')
        
        rows = cursor.fetchall()
        
        conn.close()
        
        return [Dish.from_db_row(tuple(row)) for row in rows]
    
    def delete_dish(self, dish_id):
        """Delete a dish by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    # Menu operations
    def save_menu(self, menu):
        """Save a menu to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if menu.id is None:
            # Insert new menu
            cursor.execute('''
            INSERT INTO menus (user_id, name, creation_date, cuisine_type, 
                              budget_per_meal, max_prep_time, meals)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                menu.user_id,
                menu.name,
                menu.creation_date,
                menu.cuisine_type,
                menu.budget_per_meal,
                menu.max_prep_time,
                json.dumps(menu.meals)
            ))
            menu.id = cursor.lastrowid
        else:
            # Update existing menu
            cursor.execute('''
            UPDATE menus
            SET user_id = ?, name = ?, creation_date = ?, cuisine_type = ?,
                budget_per_meal = ?, max_prep_time = ?, meals = ?
            WHERE id = ?
            ''', (
                menu.user_id,
                menu.name,
                menu.creation_date,
                menu.cuisine_type,
                menu.budget_per_meal,
                menu.max_prep_time,
                json.dumps(menu.meals),
                menu.id
            ))
        
        conn.commit()
        conn.close()
        return menu
    
    def get_menu(self, menu_id):
        """Get a menu by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM menus WHERE id = ?', (menu_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return Menu.from_db_row(tuple(row))
        return None
    
    def get_user_menus(self, user_id):
        """Get all menus for a specific user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM menus WHERE user_id = ? ORDER BY creation_date DESC', (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [Menu.from_db_row(tuple(row)) for row in rows]
    
    def get_all_menus(self, cuisine_type=None):
        """Get all menus, optionally filtered by cuisine type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if cuisine_type:
            cursor.execute('SELECT * FROM menus WHERE cuisine_type = ? ORDER BY creation_date DESC', (cuisine_type,))
        else:
            cursor.execute('SELECT * FROM menus ORDER BY creation_date DESC')
        
        rows = cursor.fetchall()
        
        conn.close()
        
        return [Menu.from_db_row(tuple(row)) for row in rows]
    
    def delete_menu(self, menu_id):
        """Delete a menu by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM menus WHERE id = ?', (menu_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    # Recipe operations
    def save_recipe(self, name, content, cuisine_type=None):
        """Save a recipe to the database.
        
        Args:
            name: Name of the recipe
            content: JSON string of recipe data
            cuisine_type: Type of cuisine
            
        Returns:
            Recipe: The saved recipe object
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if recipe already exists
        cursor.execute('SELECT id FROM recipes WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        recipe = Recipe(name=name, content=content, cuisine_type=cuisine_type)
        
        if row:
            # Update existing recipe
            recipe.id = row[0]
            cursor.execute('''
            UPDATE recipes
            SET content = ?, cuisine_type = ?, creation_date = ?
            WHERE id = ?
            ''', (
                content,
                cuisine_type,
                recipe.creation_date,
                recipe.id
            ))
        else:
            # Insert new recipe
            cursor.execute('''
            INSERT INTO recipes (name, cuisine_type, content, creation_date)
            VALUES (?, ?, ?, ?)
            ''', (
                name,
                cuisine_type,
                content,
                recipe.creation_date
            ))
            recipe.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return recipe
    
    def get_recipe(self, recipe_id):
        """Get a recipe by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return Recipe.from_db_row(tuple(row))
        return None
    
    def get_recipe_by_name(self, name):
        """Get a recipe by name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recipes WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return Recipe.from_db_row(tuple(row))
        return None
    
    def get_all_recipes(self, cuisine_type=None):
        """Get all recipes, optionally filtered by cuisine type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if cuisine_type:
            cursor.execute('SELECT * FROM recipes WHERE cuisine_type = ?', (cuisine_type,))
        else:
            cursor.execute('SELECT * FROM recipes ORDER BY name')
        
        rows = cursor.fetchall()
        
        conn.close()
        
        return [Recipe.from_db_row(tuple(row)) for row in rows]
    
    def delete_recipe(self, recipe_id):
        """Delete a recipe by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0 