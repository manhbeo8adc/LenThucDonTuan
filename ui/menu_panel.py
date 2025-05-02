"""
Menu panel for displaying and managing the weekly menu.
"""
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QProgressBar, QDialog,
    QTextEdit, QComboBox, QSpinBox, QGroupBox, QSplitter, QFrame, QHeaderView,
    QFileDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QColor

from database.models import User, Menu
from utils.helpers import format_currency, format_time
from utils.ingredient_optimizer import IngredientOptimizer


class MenuPanel(QWidget):
    """Panel for generating and displaying the weekly menu."""
    
    def __init__(self, api, db_manager):
        """Initialize the panel."""
        super().__init__()
        
        self.api = api
        self.db_manager = db_manager
        
        self.user = None
        self.cuisine_type = None
        self.budget_settings = None
        
        self.current_menu = {}
        self.optimization_notes = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Thực đơn tuần")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Setup status
        self.setup_status_layout = QHBoxLayout()
        
        self.user_status_label = QLabel("Người dùng: Chưa chọn")
        self.cuisine_status_label = QLabel("Phong cách ẩm thực: Chưa chọn")
        self.budget_status_label = QLabel("Ngân sách và thời gian: Chưa thiết lập")
        
        self.setup_status_layout.addWidget(self.user_status_label)
        self.setup_status_layout.addWidget(self.cuisine_status_label)
        self.setup_status_layout.addWidget(self.budget_status_label)
        
        main_layout.addLayout(self.setup_status_layout)
        
        # Generate menu button
        generate_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Tạo thực đơn")
        self.generate_button.clicked.connect(self._generate_menu)
        self.generate_button.setEnabled(False)
        
        generate_layout.addStretch()
        generate_layout.addWidget(self.generate_button)
        
        main_layout.addLayout(generate_layout)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Menu content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tab widget for days
        self.days_tab_widget = QTabWidget()
        
        # Optimization panel
        optimization_panel = QGroupBox("Tối ưu hóa nguyên liệu")
        optimization_layout = QVBoxLayout(optimization_panel)
        
        self.optimization_notes_label = QLabel("Các ghi chú tối ưu hóa nguyên liệu:")
        optimization_layout.addWidget(self.optimization_notes_label)
        
        self.optimization_notes_text = QTextEdit()
        self.optimization_notes_text.setReadOnly(True)
        optimization_layout.addWidget(self.optimization_notes_text)
        
        # Add widgets to splitter
        splitter.addWidget(self.days_tab_widget)
        splitter.addWidget(optimization_panel)
        
        # Set initial sizes
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Xóa thực đơn")
        self.clear_button.clicked.connect(self.clear_menu)
        self.clear_button.setEnabled(False)
        
        self.edit_button = QPushButton("Chỉnh sửa thực đơn")
        self.edit_button.clicked.connect(self._edit_menu)
        self.edit_button.setEnabled(False)
        
        self.view_recipe_button = QPushButton("Xem công thức")
        self.view_recipe_button.clicked.connect(self._view_recipe)
        self.view_recipe_button.setEnabled(False)
        
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.view_recipe_button)
        
        main_layout.addLayout(buttons_layout)
    
    @pyqtSlot(User)
    def set_user(self, user):
        """Set the user."""
        self.user = user
        self.user_status_label.setText(f"Người dùng: {user.name}")
        self._check_generate_button()
    
    @pyqtSlot(str)
    def set_cuisine(self, cuisine_type):
        """Set the cuisine type."""
        self.cuisine_type = cuisine_type
        self.cuisine_status_label.setText(f"Phong cách ẩm thực: {cuisine_type}")
        self._check_generate_button()
    
    @pyqtSlot(dict)
    def set_budget_settings(self, settings):
        """Set the budget settings."""
        self.budget_settings = settings
        
        budget_text = format_currency(settings["budget_per_meal"])
        time_text = format_time(settings["max_prep_time"])
        days_count = len(settings["days"])
        meals_count = len(settings["meals_per_day"])
        
        self.budget_status_label.setText(
            f"Ngân sách: {budget_text}, Thời gian: {time_text}, "
            f"Ngày: {days_count}, Bữa ăn: {meals_count}"
        )
        
        self._check_generate_button()
    
    def _check_generate_button(self):
        """Check if the generate button should be enabled."""
        self.generate_button.setEnabled(
            self.user is not None and
            self.cuisine_type is not None and
            self.budget_settings is not None
        )
    
    def _generate_menu(self):
        """Generate the weekly menu."""
        if not self.user or not self.cuisine_type or not self.budget_settings:
            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng chọn người dùng, phong cách ẩm thực và thiết lập ngân sách."
            )
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.generate_button.setEnabled(False)
        
        # Call API to generate menu
        days = self.budget_settings["days"]
        meals_per_day = self.budget_settings["meals_per_day"]
        budget_per_meal = self.budget_settings["budget_per_meal"]
        max_prep_time = self.budget_settings["max_prep_time"]
        
        try:
            # In a real application, this would be done in a separate thread
            result = self.api.generate_weekly_menu(
                self.user,
                self.cuisine_type,
                budget_per_meal,
                max_prep_time,
                days,
                meals_per_day
            )
            
            # Check for errors
            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"]
                if "429" in str(error_msg):
                    QMessageBox.critical(
                        self,
                        "Lỗi API",
                        "Tài khoản OpenAI của bạn đã hết hạn mức sử dụng. "
                        "Vui lòng:\n"
                        "1. Kiểm tra và nạp thêm credit vào tài khoản\n"
                        "2. Hoặc tạo API key mới\n"
                        "3. Hoặc đợi đến khi quota được reset\n\n"
                        "Chi tiết lỗi: " + str(error_msg)
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Lỗi",
                        f"Lỗi khi tạo thực đơn: {error_msg}"
                    )
                return
            
            # Process and display the menu
            if "menu" in result:
                self.current_menu = result["menu"]
                self.optimization_notes = result.get("optimization_notes", [])
                
                self._display_menu()
                
                # Enable buttons
                self.clear_button.setEnabled(True)
                self.edit_button.setEnabled(True)
                self.view_recipe_button.setEnabled(True)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Có lỗi xảy ra khi tạo thực đơn: {str(e)}"
            )
        finally:
            # Hide progress
            self.progress_bar.setVisible(False)
            self.generate_button.setEnabled(True)
    
    def _display_menu(self):
        """Display the generated menu."""
        # Clear previous tabs
        self.days_tab_widget.clear()
        
        # Display optimization notes
        self.optimization_notes_text.clear()
        for note in self.optimization_notes:
            self.optimization_notes_text.append(f"• {note}")
        
        # Create tabs for each day
        for day, meals in self.current_menu.items():
            # Skip non-day keys
            if day == "optimization_notes":
                continue
                
            # Create table for this day
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels([
                "Bữa ăn", "Món ăn", "Nguyên liệu", "Thời gian", "Chi phí"
            ])
            
            # Set row count based on number of meals
            table.setRowCount(len(meals))
            
            # Populate table
            for row, (meal_time, meal_info) in enumerate(meals.items()):
                # Meal time
                meal_time_item = QTableWidgetItem(meal_time)
                table.setItem(row, 0, meal_time_item)
                
                # Dish name
                dish_name_item = QTableWidgetItem(meal_info["name"])
                table.setItem(row, 1, dish_name_item)
                
                # Ingredients
                ingredients_text = ", ".join(meal_info["ingredients"])
                ingredients_item = QTableWidgetItem(ingredients_text)
                
                # Highlight reused ingredients
                if "reused_ingredients" in meal_info and meal_info["reused_ingredients"]:
                    ingredients_item.setBackground(QColor(230, 255, 230))  # Light green
                
                table.setItem(row, 2, ingredients_item)
                
                # Preparation time
                prep_time_text = format_time(meal_info["preparation_time"])
                prep_time_item = QTableWidgetItem(prep_time_text)
                table.setItem(row, 3, prep_time_item)
                
                # Cost
                cost_text = format_currency(meal_info["estimated_cost"])
                cost_item = QTableWidgetItem(cost_text)
                table.setItem(row, 4, cost_item)
            
            # Adjust column widths
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            
            # Add the table as a tab
            self.days_tab_widget.addTab(table, day)
    
    def _edit_menu(self):
        """Edit the current menu."""
        if not self.current_menu:
            return
        
        # Get the current day and meal from the table
        current_tab_index = self.days_tab_widget.currentIndex()
        if current_tab_index < 0:
            return
        
        current_day = self.days_tab_widget.tabText(current_tab_index)
        
        # Get the current table
        table = self.days_tab_widget.widget(current_tab_index)
        if not table:
            return
        
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self,
                "Chọn món ăn",
                "Vui lòng chọn một món ăn để chỉnh sửa."
            )
            return
        
        # Get the meal time from the table
        meal_time_item = table.item(current_row, 0)
        if not meal_time_item:
            return
        
        meal_time = meal_time_item.text()
        
        # Get the current meal info
        if current_day not in self.current_menu or meal_time not in self.current_menu[current_day]:
            return
        
        meal_info = self.current_menu[current_day][meal_time]
        
        # Create and show the edit dialog
        dialog = MealEditDialog(self, meal_info, self.cuisine_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update the meal info
            updated_meal = dialog.get_meal_info()
            self.current_menu[current_day][meal_time] = updated_meal
            
            # Update the table
            dish_name_item = QTableWidgetItem(updated_meal["name"])
            table.setItem(current_row, 1, dish_name_item)
            
            ingredients_text = ", ".join(updated_meal["ingredients"])
            ingredients_item = QTableWidgetItem(ingredients_text)
            
            if "reused_ingredients" in updated_meal and updated_meal["reused_ingredients"]:
                ingredients_item.setBackground(QColor(230, 255, 230))  # Light green
                
            table.setItem(current_row, 2, ingredients_item)
            
            prep_time_text = format_time(updated_meal["preparation_time"])
            prep_time_item = QTableWidgetItem(prep_time_text)
            table.setItem(current_row, 3, prep_time_item)
            
            cost_text = format_currency(updated_meal["estimated_cost"])
            cost_item = QTableWidgetItem(cost_text)
            table.setItem(current_row, 4, cost_item)
    
    def _view_recipe(self):
        """View the recipe for the selected meal."""
        if not self.current_menu:
            return
        
        # Get the current day and meal from the table
        current_tab_index = self.days_tab_widget.currentIndex()
        if current_tab_index < 0:
            return
        
        current_day = self.days_tab_widget.tabText(current_tab_index)
        
        # Get the current table
        table = self.days_tab_widget.widget(current_tab_index)
        if not table:
            return
        
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self,
                "Chọn món ăn",
                "Vui lòng chọn một món ăn để xem công thức."
            )
            return
        
        # Get the meal time from the table
        meal_time_item = table.item(current_row, 0)
        if not meal_time_item:
            return
        
        meal_time = meal_time_item.text()
        
        # Get the current meal info
        if current_day not in self.current_menu or meal_time not in self.current_menu[current_day]:
            return
        
        meal_info = self.current_menu[current_day][meal_time]
        
        # Show progress
        self.progress_bar.setVisible(True)
        
        # Generate recipe
        recipe = self.api.generate_recipe(meal_info["name"], self.cuisine_type)
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        # Check for errors
        if "error" in recipe:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Lỗi khi tạo công thức: {recipe['error']}"
            )
            return
        
        # Display recipe
        dialog = RecipeDialog(self, recipe, meal_info["name"])
        dialog.exec()
    
    def clear_menu(self):
        """Clear the current menu."""
        self.current_menu = {}
        self.optimization_notes = []
        
        # Clear UI
        self.days_tab_widget.clear()
        self.optimization_notes_text.clear()
        
        # Disable buttons
        self.clear_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.view_recipe_button.setEnabled(False)
    
    def get_menu_data(self):
        """Get the current menu data."""
        if not self.current_menu:
            return None
        
        return {
            "menu": self.current_menu,
            "optimization_notes": self.optimization_notes,
            "user_id": self.user.id if self.user else None,
            "cuisine_type": self.cuisine_type,
            "budget_per_meal": self.budget_settings["budget_per_meal"] if self.budget_settings else None,
            "max_prep_time": self.budget_settings["max_prep_time"] if self.budget_settings else None
        }
    
    def load_menu(self, data):
        """Load a menu from data."""
        if not data or "menu" not in data:
            return False
        
        self.current_menu = data["menu"]
        self.optimization_notes = data.get("optimization_notes", [])
        
        # Display the menu
        self._display_menu()
        
        # Enable buttons
        self.clear_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.view_recipe_button.setEnabled(True)
        
        return True


class MealEditDialog(QDialog):
    """Dialog for editing a meal."""
    
    def __init__(self, parent, meal_info, cuisine_type):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.meal_info = meal_info.copy()
        self.cuisine_type = cuisine_type
        
        self.setWindowTitle("Chỉnh sửa món ăn")
        self.setMinimumSize(QSize(500, 400))
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QVBoxLayout(self)
        
        # Meal name
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên món ăn:")
        self.name_edit = QLineEdit(self.meal_info["name"])
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        
        layout.addLayout(name_layout)
        
        # Ingredients
        ingredients_group = QGroupBox("Nguyên liệu")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        self.ingredients_edit = QTextEdit()
        self.ingredients_edit.setPlainText("\n".join(self.meal_info["ingredients"]))
        
        ingredients_layout.addWidget(self.ingredients_edit)
        
        layout.addWidget(ingredients_group)
        
        # Preparation time
        time_layout = QHBoxLayout()
        time_label = QLabel("Thời gian chuẩn bị (phút):")
        self.time_spin = QSpinBox()
        self.time_spin.setRange(5, 180)
        self.time_spin.setSingleStep(5)
        self.time_spin.setValue(self.meal_info["preparation_time"])
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_spin)
        
        layout.addLayout(time_layout)
        
        # Cost
        cost_layout = QHBoxLayout()
        cost_label = QLabel("Chi phí ước tính (VND):")
        self.cost_spin = QSpinBox()
        self.cost_spin.setRange(10000, 500000)
        self.cost_spin.setSingleStep(5000)
        self.cost_spin.setValue(self.meal_info["estimated_cost"])
        
        cost_layout.addWidget(cost_label)
        cost_layout.addWidget(self.cost_spin)
        
        layout.addLayout(cost_layout)
        
        # Reused ingredients
        reused_group = QGroupBox("Nguyên liệu tái sử dụng")
        reused_layout = QVBoxLayout(reused_group)
        
        self.reused_edit = QTextEdit()
        if "reused_ingredients" in self.meal_info:
            self.reused_edit.setPlainText("\n".join(self.meal_info["reused_ingredients"]))
        
        reused_layout.addWidget(self.reused_edit)
        
        layout.addWidget(reused_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(self.reject)
        
        save_button = QPushButton("Lưu")
        save_button.clicked.connect(self.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
    
    def get_meal_info(self):
        """Get the updated meal info."""
        # Update meal info
        self.meal_info["name"] = self.name_edit.text()
        self.meal_info["ingredients"] = [
            line.strip() for line in self.ingredients_edit.toPlainText().split("\n")
            if line.strip()
        ]
        self.meal_info["preparation_time"] = self.time_spin.value()
        self.meal_info["estimated_cost"] = self.cost_spin.value()
        
        # Reused ingredients
        reused = [
            line.strip() for line in self.reused_edit.toPlainText().split("\n")
            if line.strip()
        ]
        
        if reused:
            self.meal_info["reused_ingredients"] = reused
        elif "reused_ingredients" in self.meal_info:
            del self.meal_info["reused_ingredients"]
        
        return self.meal_info


class RecipeDialog(QDialog):
    """Dialog for displaying a recipe."""
    
    def __init__(self, parent, recipe_data, dish_name):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.recipe_data = recipe_data
        self.dish_name = dish_name
        
        self.setWindowTitle(f"Công thức: {dish_name}")
        self.setMinimumSize(QSize(600, 500))
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QVBoxLayout(self)
        
        # Recipe might be under 'recipe' key or directly in the data
        recipe = self.recipe_data.get("recipe", self.recipe_data)
        
        # Title
        title_label = QLabel(recipe.get("name", self.dish_name))
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Basic info
        info_layout = QHBoxLayout()
        
        cuisine_label = QLabel(f"<b>Phong cách:</b> {recipe.get('cuisine_type', 'Không có thông tin')}")
        prep_time_label = QLabel(f"<b>Thời gian chuẩn bị:</b> {format_time(recipe.get('preparation_time', 0))}")
        cooking_time_label = QLabel(f"<b>Thời gian nấu:</b> {format_time(recipe.get('cooking_time', 0))}")
        servings_label = QLabel(f"<b>Khẩu phần:</b> {recipe.get('servings', 1)} người")
        
        info_layout.addWidget(cuisine_label)
        info_layout.addWidget(prep_time_label)
        info_layout.addWidget(cooking_time_label)
        info_layout.addWidget(servings_label)
        
        layout.addLayout(info_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Ingredients
        ingredients_group = QGroupBox("Nguyên liệu")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        ingredients_text = QTextEdit()
        ingredients_text.setReadOnly(True)
        
        ingredients = recipe.get("ingredients", [])
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                if isinstance(ingredient, dict):
                    name = ingredient.get("name", "")
                    amount = ingredient.get("amount", "")
                    unit = ingredient.get("unit", "")
                    ingredients_text.append(f"• {name}: {amount} {unit}")
                else:
                    ingredients_text.append(f"• {ingredient}")
        else:
            ingredients_text.setPlainText(str(ingredients))
        
        ingredients_layout.addWidget(ingredients_text)
        
        layout.addWidget(ingredients_group)
        
        # Steps
        steps_group = QGroupBox("Các bước thực hiện")
        steps_layout = QVBoxLayout(steps_group)
        
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        
        steps = recipe.get("steps", [])
        if isinstance(steps, list):
            for i, step in enumerate(steps, 1):
                steps_text.append(f"{i}. {step}")
        else:
            steps_text.setPlainText(str(steps))
        
        steps_layout.addWidget(steps_text)
        
        layout.addWidget(steps_group)
        
        # Tips
        tips = recipe.get("tips", [])
        if tips:
            tips_group = QGroupBox("Mẹo")
            tips_layout = QVBoxLayout(tips_group)
            
            tips_text = QTextEdit()
            tips_text.setReadOnly(True)
            
            if isinstance(tips, list):
                for tip in tips:
                    tips_text.append(f"• {tip}")
            else:
                tips_text.setPlainText(str(tips))
            
            tips_layout.addWidget(tips_text)
            
            layout.addWidget(tips_group)
        
        # Close button
        close_button = QPushButton("Đóng")
        close_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout) 