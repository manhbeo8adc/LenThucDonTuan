"""
Menu panel for displaying and managing the weekly menu.
"""
import os
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QProgressBar, QDialog,
    QTextEdit, QComboBox, QSpinBox, QGroupBox, QSplitter, QFrame, QHeaderView,
    QFileDialog, QLineEdit, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from database.models import User, Menu, Recipe
from utils.helpers import format_currency, format_time
from utils.ingredient_optimizer import IngredientOptimizer
from ui.toast import ToastNotification

# Configure logging
logger = logging.getLogger(__name__)

# Create recipes directory if it doesn't exist
RECIPES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recipes')
if not os.path.exists(RECIPES_DIR):
    os.makedirs(RECIPES_DIR)

class MenuGeneratorWorker(QThread):
    """Worker thread for generating menu without blocking UI."""
    
    finished = pyqtSignal(dict)  # Signal emitted when generation is complete
    error = pyqtSignal(str)      # Signal emitted on error
    
    def __init__(self, api, user, cuisine_type, budget_per_meal, max_prep_time, days, meals_per_day, servings):
        """Initialize the worker."""
        super().__init__()
        self.api = api
        self.user = user
        self.cuisine_type = cuisine_type
        self.budget_per_meal = budget_per_meal
        self.max_prep_time = max_prep_time
        self.days = days
        self.meals_per_day = meals_per_day
        self.servings = servings
    
    def run(self):
        """Run the generation in a separate thread."""
        try:
            result = self.api.generate_weekly_menu(
                self.user,
                self.cuisine_type,
                self.budget_per_meal,
                self.max_prep_time,
                self.days,
                self.meals_per_day,
                self.servings
            )
            
            # Check for errors in the result
            if isinstance(result, dict) and "error" in result:
                self.error.emit(result["error"])
                return
                
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class RecipeGeneratorWorker(QThread):
    """Worker thread for generating recipes without blocking UI."""
    
    finished = pyqtSignal(dict)  # Signal emitted when generation is complete
    error = pyqtSignal(str)      # Signal emitted on error
    
    def __init__(self, api, dish_name, cuisine_type, servings=4):
        """Initialize the worker."""
        super().__init__()
        self.api = api
        self.dish_name = dish_name
        self.cuisine_type = cuisine_type
        self.servings = servings
    
    def run(self):
        """Run the generation in a separate thread."""
        try:
            result = self.api.generate_recipe(self.dish_name, self.cuisine_type, self.servings)
            
            # Check for errors in the result
            if isinstance(result, dict) and "error" in result:
                self.error.emit(result["error"])
                return
                
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


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
        
        # Add worker thread references
        self.menu_worker = None
        self.recipe_worker = None
        
        # Create toast notification
        self.toast = ToastNotification(self)
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Top section - with title, status, and action buttons
        top_section = QVBoxLayout()
        
        # Title
        title_row = QHBoxLayout()
        title_label = QLabel("Thực đơn tuần")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        top_section.addLayout(title_row)
        
        # Setup status
        self.setup_status_layout = QHBoxLayout()
        
        self.user_status_label = QLabel("Người dùng: Chưa chọn")
        self.cuisine_status_label = QLabel("Phong cách ẩm thực: Chưa chọn")
        self.budget_status_label = QLabel("Ngân sách và thời gian: Chưa thiết lập")
        
        self.setup_status_layout.addWidget(self.user_status_label)
        self.setup_status_layout.addWidget(self.cuisine_status_label)
        self.setup_status_layout.addWidget(self.budget_status_label)
        
        top_section.addLayout(self.setup_status_layout)
        
        # Generate menu button
        generate_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Tạo thực đơn")
        self.generate_button.clicked.connect(self._generate_menu)
        self.generate_button.setEnabled(False)
        
        # Add saved recipes button
        self.saved_recipes_button = QPushButton("Công thức đã lưu")
        self.saved_recipes_button.clicked.connect(self.view_saved_recipes)
        
        # Add saved menus button
        self.saved_menus_button = QPushButton("Thực đơn đã lưu")
        self.saved_menus_button.clicked.connect(self._view_saved_menus)
        
        generate_layout.addWidget(self.saved_recipes_button)
        generate_layout.addWidget(self.saved_menus_button)
        generate_layout.addStretch()
        generate_layout.addWidget(self.generate_button)
        
        top_section.addLayout(generate_layout)
        
        # Add top section to main layout
        main_layout.addLayout(top_section)
        
        # Progress indicators (initially hidden)
        self.progress_container = QFrame()
        progress_layout = QVBoxLayout(self.progress_container)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: #3366cc;")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_container.setVisible(False)
        main_layout.addWidget(self.progress_container)
        
        # Main content - create a splitter for menu and optimization
        main_content = QSplitter(Qt.Orientation.Horizontal)
        main_content.setChildrenCollapsible(False)
        
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
        main_content.addWidget(self.days_tab_widget)
        main_content.addWidget(optimization_panel)
        
        # Set initial sizes for the splitter (wider menu, narrower optimization panel)
        main_content.setSizes([700, 300])
        
        # Add to main layout with a stretch factor of 1 to make it take available space
        main_layout.addWidget(main_content, 1)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Xóa thực đơn")
        self.clear_button.clicked.connect(self.clear_menu)
        self.clear_button.setEnabled(False)
        
        self.save_menu_button = QPushButton("Lưu thực đơn")
        self.save_menu_button.clicked.connect(self._save_current_menu)
        self.save_menu_button.setEnabled(False)
        
        self.edit_button = QPushButton("Chỉnh sửa thực đơn")
        self.edit_button.clicked.connect(self._edit_menu)
        self.edit_button.setEnabled(False)
        
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.save_menu_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.edit_button)
        
        main_layout.addLayout(buttons_layout)
    
    @pyqtSlot(User)
    def set_user(self, user):
        """Set the user."""
        try:
            logger.info(f"Setting user: {user.name}")
            self.user = user
            self.user_status_label.setText(f"Người dùng: {user.name}")
            self._check_generate_button()
            self.toast.show_message(f"Đã chọn người dùng: {user.name}")
            logger.info("User set successfully")
        except Exception as e:
            logger.error(f"Error setting user: {str(e)}")
            raise
    
    @pyqtSlot(str)
    def set_cuisine(self, cuisine_type):
        """Set the cuisine type."""
        try:
            logger.info(f"Setting cuisine type: {cuisine_type}")
            self.cuisine_type = cuisine_type
            self.cuisine_status_label.setText(f"Phong cách ẩm thực: {cuisine_type}")
            self._check_generate_button()
            self.toast.show_message(f"Đã chọn phong cách ẩm thực: {cuisine_type}")
            logger.info("Cuisine type set successfully")
        except Exception as e:
            logger.error(f"Error setting cuisine type: {str(e)}")
            raise
    
    @pyqtSlot(dict)
    def set_budget_settings(self, settings):
        """Set the budget settings."""
        try:
            logger.info("Setting budget settings")
            self.budget_settings = settings
            budget_text = format_currency(settings['budget_per_meal'])
            prep_time_text = format_time(settings['max_prep_time'])
            self.budget_status_label.setText(f"Ngân sách: {budget_text} - Thời gian: {prep_time_text}")
            self._check_generate_button()
            self.toast.show_message("Đã áp dụng thiết lập thành công!")
            logger.info("Budget settings set successfully")
        except Exception as e:
            logger.error(f"Error setting budget settings: {str(e)}")
            raise
    
    def _check_generate_button(self):
        """Check if the generate button should be enabled."""
        self.generate_button.setEnabled(
            self.user is not None and
            self.cuisine_type is not None and
            self.budget_settings is not None
        )
    
    def _generate_menu(self):
        """Generate a new menu."""
        if not self.user or not self.cuisine_type or not self.budget_settings:
            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng cung cấp đầy đủ thông tin về người dùng, phong cách ẩm thực và ngân sách."
            )
            return
        
        # Show progress indicators
        self.progress_container.setVisible(True)
        self._update_status_label("Đang chuẩn bị tạo thực đơn tuần...")
        
        # Disable generate button
        self.generate_button.setEnabled(False)
        
        # Connect to API progress signal before creating worker
        self.api.progress_signal.connect(self._update_status_label)
        
        # Create worker thread for menu generation
        self.menu_worker = MenuGeneratorWorker(
            self.api,
            self.user,
            self.cuisine_type,
            self.budget_settings["budget_per_meal"],
            self.budget_settings["max_prep_time"],
            self.budget_settings["days"],
            self.budget_settings["meals_per_day"],
            self.budget_settings.get("servings", 4)  # Sử dụng thông tin khẩu phần, mặc định là 4 nếu không có
        )
        
        # Connect signals
        self.menu_worker.finished.connect(self._handle_menu_result)
        self.menu_worker.error.connect(self._handle_menu_error)
        
        # Start worker
        self.menu_worker.start()
    
    def _update_status_label(self, message):
        """Update the status label with progress information."""
        self.status_label.setText(message)
        
    def _handle_menu_result(self, result):
        """Handle the menu generation result."""
        # Process and display the menu
        if "menu" in result:
            self.current_menu = result["menu"]
            self.optimization_notes = result.get("optimization_notes", [])
            
            self._display_menu()
            
            # Enable buttons
            self.clear_button.setEnabled(True)
            self.edit_button.setEnabled(True)
            self.save_menu_button.setEnabled(True)
        
        # Hide progress
        self.progress_container.setVisible(False)
        self.generate_button.setEnabled(True)
        
        # Safely disconnect the progress signal
        try:
            self.api.progress_signal.disconnect(self._update_status_label)
        except TypeError:
            # Signal was not connected
            logger.info("Progress signal was not connected")
            pass
    
    def _handle_menu_error(self, error_msg):
        """Handle menu generation error."""
        # Hide progress
        self.progress_container.setVisible(False)
        self.generate_button.setEnabled(True)
        
        # Safely disconnect the progress signal
        try:
            self.api.progress_signal.disconnect(self._update_status_label)
        except TypeError:
            # Signal was not connected
            logger.info("Progress signal was not connected")
            pass
        
        # Show error message
        if "429" in error_msg:
            QMessageBox.critical(
                self,
                "Lỗi API",
                "Tài khoản OpenAI của bạn đã hết hạn mức sử dụng. "
                "Vui lòng:\n"
                "1. Kiểm tra và nạp thêm credit vào tài khoản\n"
                "2. Hoặc tạo API key mới\n"
                "3. Hoặc đợi đến khi quota được reset\n\n"
                "Chi tiết lỗi: " + error_msg
            )
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Lỗi khi tạo thực đơn: {error_msg}"
            )
    
    def _create_meal_info_panel(self, meal_info):
        """Create a panel showing detailed meal information."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        layout = QVBoxLayout(panel)
        # Add more spacing for better readability
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Top info layout
        top_layout = QHBoxLayout()
        
        # Dish name and basic info
        info_layout = QVBoxLayout()
        name_label = QLabel(f"<b>{meal_info['name']}</b>")
        name_label.setStyleSheet("font-size: 14px;")
        name_label.setWordWrap(True)  # Enable word wrap
        info_layout.addWidget(name_label)
        
        # Time and cost
        details_label = QLabel(
            f"Thời gian chuẩn bị: {format_time(meal_info['preparation_time'])} | "
            f"Chi phí ước tính: {format_currency(meal_info['estimated_cost'])}"
        )
        details_label.setStyleSheet("color: #666;")
        details_label.setWordWrap(True)  # Enable word wrap
        info_layout.addWidget(details_label)
        
        top_layout.addLayout(info_layout)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Create a scroll area for detailed information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        
        # Create two columns for information
        info_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        
        # Left column: Nutrition and Cooking Method
        if 'nutrition_info' in meal_info:
            nutrition_group = QGroupBox("Thông tin dinh dưỡng")
            nutrition_layout = QVBoxLayout(nutrition_group)
            
            nutrition = meal_info['nutrition_info']
            nutrition_text = QLabel(
                f"Protein: {nutrition.get('protein', 'N/A')}\n"
                f"Carbs: {nutrition.get('carbs', 'N/A')}\n"
                f"Chất béo: {nutrition.get('fat', 'N/A')}\n"
                f"Calories: {nutrition.get('calories', 'N/A')}"
            )
            nutrition_text.setWordWrap(True)  # Enable word wrap
            nutrition_layout.addWidget(nutrition_text)
            left_column.addWidget(nutrition_group)
        
        if 'cooking_method' in meal_info:
            method_group = QGroupBox("Phương pháp nấu")
            method_layout = QVBoxLayout(method_group)
            method_label = QLabel(", ".join(meal_info['cooking_method']) if isinstance(meal_info['cooking_method'], list) else meal_info['cooking_method'])
            method_label.setWordWrap(True)
            method_layout.addWidget(method_label)
            
            # Add view recipe button
            view_recipe_btn = QPushButton("Xem công thức chi tiết")
            view_recipe_btn.setStyleSheet("""
                QPushButton {
                    font-size: 11pt;
                    padding: 5px 10px;
                    border-radius: 4px;
                    background-color: #DB7093;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #C1638A;
                }
                QPushButton:pressed {
                    background-color: #A5547B;
                }
            """)
            view_recipe_btn.clicked.connect(lambda: self._view_recipe_for_meal(meal_info))
            method_layout.addWidget(view_recipe_btn)
            
            left_column.addWidget(method_group)
        
        # Right column: Food Groups and Reused Ingredients
        if 'food_groups' in meal_info:
            groups_group = QGroupBox("Nhóm thực phẩm")
            groups_layout = QVBoxLayout(groups_group)
            groups_label = QLabel(", ".join(meal_info['food_groups']))
            groups_label.setWordWrap(True)
            groups_layout.addWidget(groups_label)
            right_column.addWidget(groups_group)
        
        if 'reused_ingredients' in meal_info:
            reused_group = QGroupBox("Nguyên liệu tái sử dụng")
            reused_layout = QVBoxLayout(reused_group)
            reused_label = QLabel(", ".join(meal_info['reused_ingredients']))
            reused_label.setWordWrap(True)
            reused_layout.addWidget(reused_label)
            right_column.addWidget(reused_group)
        
        # Add ingredients list
        if 'ingredients' in meal_info:
            ingredients_group = QGroupBox("Nguyên liệu")
            ingredients_layout = QVBoxLayout(ingredients_group)
            ingredients_label = QLabel(", ".join(meal_info['ingredients']))
            ingredients_label.setWordWrap(True)
            ingredients_layout.addWidget(ingredients_label)
            right_column.addWidget(ingredients_group)
        
        # Add columns to info layout
        info_layout.addLayout(left_column)
        info_layout.addLayout(right_column)
        scroll_layout.addLayout(info_layout)
        
        # Set up the scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        return panel
    
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
            day_widget = QWidget()
            # Use QScrollArea for day content to ensure it doesn't get cut off
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QFrame.NoFrame)
            
            day_content = QWidget()
            day_layout = QVBoxLayout(day_content)
            day_layout.setSpacing(10)  # Increase spacing between meal sections
            
            # Create a widget for each meal
            for meal_type, meal_info in meals.items():
                meal_group = QGroupBox(meal_type)
                meal_layout = QVBoxLayout(meal_group)
                meal_layout.setContentsMargins(8, 12, 8, 12)  # Add more padding
                
                # Add detailed meal info panel
                meal_info_panel = self._create_meal_info_panel(meal_info)
                meal_layout.addWidget(meal_info_panel)
                
                day_layout.addWidget(meal_group)
            
            # Set up the scroll area
            scroll_area.setWidget(day_content)
            
            # Add scroll area to day widget
            day_widget_layout = QVBoxLayout(day_widget)
            day_widget_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
            day_widget_layout.addWidget(scroll_area)
            
            # Add the day widget as a new tab
            self.days_tab_widget.addTab(day_widget, day)
    
    def _edit_menu(self):
        """Edit the current menu."""
        if not self.current_menu:
            return
        
        # Get the current day
        current_tab_index = self.days_tab_widget.currentIndex()
        if current_tab_index < 0:
            return
        
        current_day = self.days_tab_widget.tabText(current_tab_index)
        
        # Show dialog to select meal
        meal_times = list(self.current_menu[current_day].keys())
        if not meal_times:
            return
            
        if len(meal_times) == 1:
            selected_meal = meal_times[0]
        else:
            # Create a simple dialog to select the meal
            dialog = QDialog(self)
            dialog.setWindowTitle("Chọn bữa ăn")
            layout = QVBoxLayout(dialog)
            
            label = QLabel("Chọn bữa ăn để chỉnh sửa:")
            layout.addWidget(label)
            
            combo = QComboBox()
            combo.setStyleSheet("""
                QComboBox {
                    font-size: 12pt;
                    padding: 5px;
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    color: black;
                    background-color: white;
                }
                QComboBox::drop-down {
                    width: 30px;
                    border: none;
                    background-color: transparent;
                }
                QComboBox:hover {
                    border: 1px solid #DB7093;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 1px solid #CCCCCC;
                    color: black;
                    selection-background-color: #DB7093;
                    selection-color: white;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    min-height: 30px;
                    padding: 5px;
                    border: none;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #DB7093;
                    color: white;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #FFF0F5;
                    color: black;
                    border: none;
                }
            """)
            for meal_time in meal_times:
                meal_name = self.current_menu[current_day][meal_time]["name"]
                combo.addItem(f"{meal_time}: {meal_name}", meal_time)
            layout.addWidget(combo)
            
            buttons = QHBoxLayout()
            cancel_btn = QPushButton("Hủy")
            cancel_btn.clicked.connect(dialog.reject)
            ok_btn = QPushButton("Chỉnh sửa")
            ok_btn.clicked.connect(dialog.accept)
            buttons.addWidget(cancel_btn)
            buttons.addWidget(ok_btn)
            layout.addLayout(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_meal = combo.currentData()
            else:
                return
        
        # Get the current meal info
        if current_day not in self.current_menu or selected_meal not in self.current_menu[current_day]:
            return
        
        meal_info = self.current_menu[current_day][selected_meal]
        
        # Create and show the edit dialog
        dialog = MealEditDialog(self, meal_info, self.cuisine_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update the meal info
            updated_meal = dialog.get_meal_info()
            self.current_menu[current_day][selected_meal] = updated_meal
            
            # Update the display
            self._display_menu()
            
            # Set the current tab back to the day we were editing
            self.days_tab_widget.setCurrentIndex(current_tab_index)
    
    def _view_recipe_for_meal(self, meal_info):
        """View recipe for a specific meal."""
        import logging
        logger = logging.getLogger(__name__)
        try:
            logger.info(f"[VIEW RECIPE] Bắt đầu xem công thức cho món: {meal_info.get('name')}")
            dish_name = meal_info["name"]
            servings = meal_info.get("servings", 4)
            if self.budget_settings and "servings" in self.budget_settings:
                servings = self.budget_settings["servings"]
            recipe = self.db_manager.get_recipe_by_name(dish_name)
            if recipe:
                self.status_label.setText(f"Hiển thị công thức đã lưu cho món {dish_name}")
                try:
                    recipe_data = json.loads(recipe.content)
                    if "recipe" in recipe_data and "servings" in recipe_data["recipe"]:
                        recipe_data["recipe"]["servings"] = servings
                    dialog = RecipeDialog(self, recipe_data, dish_name)
                    dialog.exec()
                    logger.info(f"[VIEW RECIPE] Đã hiển thị công thức đã lưu cho món: {dish_name}")
                    return
                except Exception as e:
                    logger.error(f"[VIEW RECIPE] Lỗi khi load công thức đã lưu: {e}")
            self.status_label.setText(f"Đang tạo công thức cho món {dish_name}... Vui lòng đợi")
            self.progress_container.setVisible(True)
            self.api.progress_signal.connect(self._update_status_label)
            self.recipe_worker = RecipeGeneratorWorker(
                self.api,
                dish_name,
                self.cuisine_type,
                servings
            )
            self.recipe_worker.finished.connect(lambda recipe_data: self._handle_recipe_result(recipe_data, dish_name))
            self.recipe_worker.error.connect(self._handle_recipe_error)
            self.recipe_worker.start()
            logger.info(f"[VIEW RECIPE] Đã bắt đầu tạo công thức mới cho món: {dish_name}")
        except Exception as e:
            logger.error(f"[VIEW RECIPE] Lỗi tổng quát khi xem công thức: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _handle_recipe_result(self, recipe_data, dish_name):
        """Handle the recipe generation result."""
        # Hide progress
        self.progress_container.setVisible(False)
        
        # Safely disconnect the progress signal
        try:
            self.api.progress_signal.disconnect(self._update_status_label)
        except TypeError:
            # Signal was not connected
            pass
        
        # Save recipe to database
        try:
            recipe_json = json.dumps(recipe_data, ensure_ascii=False)
            self.db_manager.save_recipe(dish_name, recipe_json, self.cuisine_type)
        except Exception as e:
            print(f"Error saving recipe to database: {e}")
        
        # Display recipe
        dialog = RecipeDialog(self, recipe_data, dish_name)
        dialog.exec()
    
    def _handle_recipe_error(self, error_msg):
        """Handle recipe generation error."""
        # Hide progress
        self.progress_container.setVisible(False)
        
        # Safely disconnect the progress signal
        try:
            self.api.progress_signal.disconnect(self._update_status_label)
        except TypeError:
            # Signal was not connected
            pass
        
        # Show error message
        QMessageBox.critical(
            self,
            "Lỗi",
            f"Lỗi khi tạo công thức: {error_msg}"
        )
    
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
        self.save_menu_button.setEnabled(False)
    
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
        self.save_menu_button.setEnabled(True)
        
        return True

    def view_saved_recipes(self):
        """Open dialog to view saved recipes."""
        dialog = SavedRecipesDialog(self, self.db_manager)
        dialog.exec()

    def _save_current_menu(self):
        """Save the current menu to the database."""
        if not self.current_menu:
            return
        
        # Create a dialog to get menu name
        dialog = QDialog(self)
        dialog.setWindowTitle("Lưu thực đơn")
        layout = QVBoxLayout(dialog)
        
        # Menu name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên thực đơn:")
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Nhập tên cho thực đơn...")
        
        current_date = datetime.now().strftime("%d/%m/%Y")
        default_name = f"Thực đơn tuần - {current_date}"
        name_edit.setText(default_name)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Lưu")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        layout.addLayout(buttons_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            menu_name = name_edit.text().strip()
            if not menu_name:
                menu_name = default_name
            
            try:
                # Create a Menu object
                menu = Menu(
                    user_id=self.user.id if self.user else None,
                    name=menu_name,
                    cuisine_type=self.cuisine_type,
                    budget_per_meal=self.budget_settings["budget_per_meal"] if self.budget_settings else None,
                    max_prep_time=self.budget_settings["max_prep_time"] if self.budget_settings else None,
                    meals=json.dumps(self.current_menu)
                )
                
                # Save to database
                saved_menu = self.db_manager.save_menu(menu)
                
                QMessageBox.information(
                    self,
                    "Lưu thành công",
                    f"Thực đơn '{menu_name}' đã được lưu thành công!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    f"Không thể lưu thực đơn: {str(e)}"
                )
    
    def _view_saved_menus(self):
        """View saved menus."""
        try:
            # Add debug info
            print("Opening saved menus dialog")
            
            # Check if the database has any menus before creating the dialog
            menus = self.db_manager.get_all_menus()
            if not menus:
                QMessageBox.information(
                    self,
                    "Thông báo",
                    "Chưa có thực đơn nào được lưu."
                )
                return
                
            dialog = SavedMenusDialog(self, self.db_manager)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted and dialog.selected_menu:
                # Load the selected menu
                try:
                    # Parse the meals JSON string
                    meals_json = dialog.selected_menu.meals
                    # Add Debug info
                    print(f"Loading menu: {dialog.selected_menu.name}")
                    print(f"Meals JSON: {meals_json}")
                    
                    # Make sure meals is a valid JSON string
                    if not meals_json or not isinstance(meals_json, str):
                        raise ValueError(f"Invalid meals data: {meals_json}")
                    
                    menu_data = {
                        "menu": json.loads(meals_json),
                        "optimization_notes": []
                    }
                    self.load_menu(menu_data)
                    
                    # Update status labels
                    if dialog.selected_menu.user_id:
                        user = self.db_manager.get_user(dialog.selected_menu.user_id)
                        if user:
                            self.user = user
                            self.user_status_label.setText(f"Người dùng: {user.name}")
                    
                    self.cuisine_type = dialog.selected_menu.cuisine_type
                    self.cuisine_status_label.setText(f"Phong cách ẩm thực: {self.cuisine_type}")
                    
                    if dialog.selected_menu.budget_per_meal and dialog.selected_menu.max_prep_time:
                        # Get the days and meals from the loaded menu
                        loaded_menu = json.loads(meals_json)
                        days = list(loaded_menu.keys())
                        
                        # Extract meal times from the first day if available
                        first_day = next(iter(loaded_menu)) if loaded_menu else None
                        meals_per_day = list(loaded_menu[first_day].keys()) if first_day and first_day in loaded_menu else []
                        
                        self.budget_settings = {
                            "budget_per_meal": dialog.selected_menu.budget_per_meal,
                            "max_prep_time": dialog.selected_menu.max_prep_time,
                            "days": days,
                            "meals_per_day": meals_per_day
                        }
                        
                        budget_text = format_currency(self.budget_settings["budget_per_meal"])
                        time_text = format_time(self.budget_settings["max_prep_time"])
                        days_count = len(self.budget_settings["days"])
                        meals_count = len(self.budget_settings["meals_per_day"])
                        
                        self.budget_status_label.setText(
                            f"Ngân sách: {budget_text}, Thời gian: {time_text}, "
                            f"Ngày: {days_count}, Bữa ăn: {meals_count}"
                        )
                except Exception as e:
                    # Add detailed error message
                    error_msg = f"Không thể tải thực đơn: {str(e)}\n"
                    if dialog.selected_menu and hasattr(dialog.selected_menu, 'meals'):
                        error_msg += f"Dữ liệu thực đơn: {str(dialog.selected_menu.meals)[:100]}"
                    
                    print(f"Error loading menu: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Lỗi",
                        error_msg
                    )
        except Exception as e:
            print(f"Error in _view_saved_menus: {str(e)}")
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Đã xảy ra lỗi khi mở thực đơn đã lưu: {str(e)}"
            )


class MealEditDialog(QDialog):
    """Dialog for editing a meal."""
    
    def __init__(self, parent, meal_info, cuisine_type):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.meal_info = meal_info.copy()
        self.cuisine_type = cuisine_type
        
        self.setWindowTitle("Chỉnh sửa món ăn")
        self.setMinimumSize(QSize(600, 500))
        
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
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        
        # Tab 1: Basic Info
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Ingredients
        ingredients_group = QGroupBox("Nguyên liệu")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        self.ingredients_edit = QTextEdit()
        self.ingredients_edit.setPlainText("\n".join(self.meal_info["ingredients"]))
        
        ingredients_layout.addWidget(self.ingredients_edit)
        basic_layout.addWidget(ingredients_group)
        
        # Preparation time
        time_layout = QHBoxLayout()
        time_label = QLabel("Thời gian chuẩn bị (phút):")
        self.time_spin = QSpinBox()
        self.time_spin.setRange(5, 180)
        self.time_spin.setSingleStep(5)
        self.time_spin.setValue(self.meal_info["preparation_time"])
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_spin)
        basic_layout.addLayout(time_layout)
        
        # Cost
        cost_layout = QHBoxLayout()
        cost_label = QLabel("Chi phí ước tính (VND):")
        self.cost_spin = QSpinBox()
        self.cost_spin.setRange(10000, 500000)
        self.cost_spin.setSingleStep(5000)
        self.cost_spin.setValue(self.meal_info["estimated_cost"])
        
        cost_layout.addWidget(cost_label)
        cost_layout.addWidget(self.cost_spin)
        basic_layout.addLayout(cost_layout)
        
        # Reused ingredients
        reused_group = QGroupBox("Nguyên liệu tái sử dụng")
        reused_layout = QVBoxLayout(reused_group)
        
        self.reused_edit = QTextEdit()
        if "reused_ingredients" in self.meal_info:
            self.reused_edit.setPlainText("\n".join(self.meal_info["reused_ingredients"]))
        
        reused_layout.addWidget(self.reused_edit)
        basic_layout.addWidget(reused_group)
        
        # Tab 2: Nutrition Info
        nutrition_tab = QWidget()
        nutrition_layout = QVBoxLayout(nutrition_tab)
        
        if "nutrition_info" not in self.meal_info:
            self.meal_info["nutrition_info"] = {
                "protein": "0g",
                "carbs": "0g",
                "fat": "0g",
                "calories": "0kcal"
            }
        
        nutrition_info = self.meal_info["nutrition_info"]
        
        # Protein
        protein_layout = QHBoxLayout()
        protein_label = QLabel("Protein:")
        self.protein_edit = QLineEdit(nutrition_info.get("protein", "0g"))
        protein_layout.addWidget(protein_label)
        protein_layout.addWidget(self.protein_edit)
        nutrition_layout.addLayout(protein_layout)
        
        # Carbs
        carbs_layout = QHBoxLayout()
        carbs_label = QLabel("Carbs:")
        self.carbs_edit = QLineEdit(nutrition_info.get("carbs", "0g"))
        carbs_layout.addWidget(carbs_label)
        carbs_layout.addWidget(self.carbs_edit)
        nutrition_layout.addLayout(carbs_layout)
        
        # Fat
        fat_layout = QHBoxLayout()
        fat_label = QLabel("Chất béo:")
        self.fat_edit = QLineEdit(nutrition_info.get("fat", "0g"))
        fat_layout.addWidget(fat_label)
        fat_layout.addWidget(self.fat_edit)
        nutrition_layout.addLayout(fat_layout)
        
        # Calories
        calories_layout = QHBoxLayout()
        calories_label = QLabel("Calories:")
        self.calories_edit = QLineEdit(nutrition_info.get("calories", "0kcal"))
        calories_layout.addWidget(calories_label)
        calories_layout.addWidget(self.calories_edit)
        nutrition_layout.addLayout(calories_layout)
        
        # Tab 3: Additional Info
        additional_tab = QWidget()
        additional_layout = QVBoxLayout(additional_tab)
        
        # Cooking method
        cooking_group = QGroupBox("Phương pháp nấu")
        cooking_layout = QVBoxLayout(cooking_group)
        
        self.cooking_edit = QLineEdit()
        if "cooking_method" in self.meal_info:
            if isinstance(self.meal_info["cooking_method"], list):
                self.cooking_edit.setText(", ".join(self.meal_info["cooking_method"]))
            else:
                self.cooking_edit.setText(self.meal_info["cooking_method"])
        
        cooking_layout.addWidget(self.cooking_edit)
        additional_layout.addWidget(cooking_group)
        
        # Food groups
        groups_group = QGroupBox("Nhóm thực phẩm")
        groups_layout = QVBoxLayout(groups_group)
        
        self.groups_edit = QTextEdit()
        if "food_groups" in self.meal_info:
            self.groups_edit.setPlainText("\n".join(self.meal_info["food_groups"]))
        
        groups_layout.addWidget(self.groups_edit)
        additional_layout.addWidget(groups_group)
        
        # Add tabs to tab widget
        tab_widget.addTab(basic_tab, "Thông tin cơ bản")
        tab_widget.addTab(nutrition_tab, "Dinh dưỡng")
        tab_widget.addTab(additional_tab, "Thông tin bổ sung")
        
        layout.addWidget(tab_widget)
        
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
        
        # Update nutrition info
        self.meal_info["nutrition_info"] = {
            "protein": self.protein_edit.text(),
            "carbs": self.carbs_edit.text(),
            "fat": self.fat_edit.text(),
            "calories": self.calories_edit.text()
        }
        
        # Update cooking method
        cooking_method = self.cooking_edit.text().strip()
        if cooking_method:
            self.meal_info["cooking_method"] = cooking_method
        elif "cooking_method" in self.meal_info:
            del self.meal_info["cooking_method"]
        
        # Update food groups
        food_groups = [
            line.strip() for line in self.groups_edit.toPlainText().split("\n")
            if line.strip()
        ]
        if food_groups:
            self.meal_info["food_groups"] = food_groups
        elif "food_groups" in self.meal_info:
            del self.meal_info["food_groups"]
        
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
        
        # Debug logging
        print(f"Recipe data: {recipe_data}")
        
        self.setWindowTitle(f"Công thức: {dish_name}")
        self.setMinimumSize(QSize(800, 700))  # Increased minimum size for better readability
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QVBoxLayout(self)
        # Increase spacing to make text more readable
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)  # Add more margin
        
        try:
            # Recipe might be under 'recipe' key or directly in the data
            recipe = self.recipe_data.get("recipe", self.recipe_data)
            
            # Recipe title with better styling
            title_label = QLabel(recipe.get("name", self.dish_name))
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #DB7093; margin-bottom: 10px;")
            title_label.setWordWrap(True)  # Enable word wrap for title
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # Create scroll area for content
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QFrame.NoFrame)
            
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(15)
            
            # Basic info
            info_widget = QWidget()
            info_layout = QHBoxLayout(info_widget)
            
            # Ensure all values are strings to prevent type comparison errors
            cuisine_type = str(recipe.get('cuisine_type', 'Không có thông tin'))
            
            # Handle preparation_time which could be string or int
            prep_time_value = recipe.get('preparation_time', 0)
            if isinstance(prep_time_value, str):
                try:
                    prep_time_value = int(prep_time_value)
                except (ValueError, TypeError):
                    prep_time_value = 0
            prep_time = format_time(prep_time_value)
            
            # Handle cooking_time which could be string or int
            cooking_time_value = recipe.get('cooking_time', 0)
            if isinstance(cooking_time_value, str):
                try:
                    cooking_time_value = int(cooking_time_value)
                except (ValueError, TypeError):
                    cooking_time_value = 0
            cooking_time = format_time(cooking_time_value)
            
            # Handle servings which could be string or int
            servings_value = recipe.get('servings', 1)
            if isinstance(servings_value, str):
                try:
                    servings_value = int(servings_value)
                except (ValueError, TypeError):
                    servings_value = 1
            servings = str(servings_value)
            
            # Difficulty
            difficulty = str(recipe.get('difficulty', 'Không có thông tin'))
            
            # Create styled info labels with icons
            cuisine_info = QLabel(f"🍲 Phong cách: {cuisine_type}")
            prep_info = QLabel(f"⏱️ Thời gian chuẩn bị: {prep_time}")
            cooking_info = QLabel(f"🔥 Thời gian nấu: {cooking_time}")
            servings_info = QLabel(f"👨‍👩‍👧‍👦 Khẩu phần: {servings} người")
            difficulty_info = QLabel(f"📊 Độ khó: {difficulty}")
            
            # Apply styling to info labels
            info_style = "font-size: 12pt; margin-right: 15px; color: #555555; font-weight: bold;"
            cuisine_info.setStyleSheet(info_style)
            prep_info.setStyleSheet(info_style)
            cooking_info.setStyleSheet(info_style)
            servings_info.setStyleSheet(info_style)
            difficulty_info.setStyleSheet(info_style)
            
            # Add info labels to layout
            info_layout.addWidget(cuisine_info)
            info_layout.addWidget(prep_info)
            info_layout.addWidget(cooking_info)
            info_layout.addStretch()
            
            # Second row of info
            info_widget2 = QWidget()
            info_layout2 = QHBoxLayout(info_widget2)
            info_layout2.addWidget(servings_info)
            info_layout2.addWidget(difficulty_info)
            info_layout2.addStretch()
            
            scroll_layout.addWidget(info_widget)
            scroll_layout.addWidget(info_widget2)
            
            # Add separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setStyleSheet("background-color: #F0F0F0;")
            scroll_layout.addWidget(separator)
            
            # Ingredients section
            ingredients_title = QLabel("Nguyên Liệu")
            ingredients_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2E8B57; margin-top: 10px;")
            scroll_layout.addWidget(ingredients_title)
            
            ingredients = recipe.get('ingredients', [])
            
            if ingredients:
                # Create a frame with nicer styling
                ingredients_frame = QFrame()
                ingredients_frame.setFrameShape(QFrame.StyledPanel)
                ingredients_frame.setStyleSheet("background-color: #F5FFFA; border-radius: 8px; padding: 10px;")
                ingredients_layout = QVBoxLayout(ingredients_frame)
                
                # Iterate through ingredients
                for ingredient in ingredients:
                    if isinstance(ingredient, dict):
                        # Handle structured ingredients
                        item = ingredient.get('item', '')
                        amount = ingredient.get('amount', '')
                        unit = ingredient.get('unit', '')
                        
                        if item:
                            # Format: "• Item - Amount Unit"
                            text = f"• {item}"
                            if amount and unit:
                                text += f" - {amount} {unit}"
                            elif amount:
                                text += f" - {amount}"
                            
                            ingredient_label = QLabel(text)
                            ingredient_label.setStyleSheet("font-size: 12pt; line-height: 1.5; color: #333333; margin: 3px 0;")
                            ingredients_layout.addWidget(ingredient_label)
                    else:
                        # Handle string ingredients
                        ingredient_label = QLabel(f"• {ingredient}")
                        ingredient_label.setStyleSheet("font-size: 12pt; line-height: 1.5; color: #333333; margin: 3px 0;")
                        ingredients_layout.addWidget(ingredient_label)
                
                scroll_layout.addWidget(ingredients_frame)
            else:
                no_ingredients = QLabel("Không có thông tin về nguyên liệu")
                no_ingredients.setStyleSheet("font-style: italic; color: #888888;")
                scroll_layout.addWidget(no_ingredients)
            
            # Add separator
            separator2 = QFrame()
            separator2.setFrameShape(QFrame.HLine)
            separator2.setFrameShadow(QFrame.Sunken)
            separator2.setStyleSheet("background-color: #F0F0F0;")
            scroll_layout.addWidget(separator2)
            
            # Steps section
            steps_title = QLabel("Các Bước Thực Hiện")
            steps_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #DB7093; margin-top: 10px;")
            scroll_layout.addWidget(steps_title)
            
            steps = recipe.get('steps', [])
            
            if steps:
                # Create a frame with nicer styling for steps
                steps_frame = QFrame()
                steps_frame.setFrameShape(QFrame.StyledPanel)
                steps_frame.setStyleSheet("background-color: #FFF5F5; border-radius: 8px; padding: 12px;")
                steps_layout = QVBoxLayout(steps_frame)
                
                # Add more spacing between steps
                steps_layout.setSpacing(15)
                
                for step in steps:
                    if isinstance(step, dict):
                        # Handle structured steps
                        step_number = step.get('step', '')
                        description = step.get('description', '')
                        
                        if description:
                            # Create a container for each step
                            step_container = QWidget()
                            step_container_layout = QVBoxLayout(step_container)
                            step_container_layout.setContentsMargins(5, 5, 5, 10)
                            
                            # Step number label
                            step_number_label = QLabel(f"Bước {step_number}")
                            step_number_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #DB7093;")
                            step_container_layout.addWidget(step_number_label)
                            
                            # Step description with better line height
                            description_label = QLabel(description)
                            description_label.setWordWrap(True)
                            description_label.setStyleSheet("font-size: 12pt; line-height: 1.6; color: #333333; margin-left: 15px;")
                            step_container_layout.addWidget(description_label)
                            
                            steps_layout.addWidget(step_container)
                            
                            # Add a subtle separator between steps
                            if step != steps[-1]:  # Don't add after the last step
                                step_separator = QFrame()
                                step_separator.setFrameShape(QFrame.HLine)
                                step_separator.setFrameShadow(QFrame.Sunken)
                                step_separator.setStyleSheet("background-color: #F0F0F0; max-height: 1px;")
                                steps_layout.addWidget(step_separator)
                    else:
                        # Handle string steps
                        step_label = QLabel(step)
                        step_label.setWordWrap(True)
                        step_label.setStyleSheet("font-size: 12pt; line-height: 1.6; color: #333333; margin: 5px 0;")
                        steps_layout.addWidget(step_label)
                
                scroll_layout.addWidget(steps_frame)
            else:
                no_steps = QLabel("Không có thông tin về các bước thực hiện")
                no_steps.setStyleSheet("font-style: italic; color: #888888;")
                scroll_layout.addWidget(no_steps)
            
            # Add extra spacing at the bottom
            scroll_layout.addStretch()
            
            scroll_area.setWidget(scroll_content)
            layout.addWidget(scroll_area, 1)  # Give scroll area all available space
            
            # Buttons
            buttons_layout = QHBoxLayout()
            close_button = QPushButton("Đóng")
            close_button.clicked.connect(self.close)
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_button)
            layout.addLayout(buttons_layout)
            
        except Exception as e:
            # Show error message
            error_label = QLabel(f"Lỗi hiển thị công thức: {str(e)}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)
            
            close_button = QPushButton("Đóng")
            close_button.clicked.connect(self.close)
            
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_button)
            
            layout.addLayout(buttons_layout)
    

class SavedRecipesDialog(QDialog):
    """Dialog for viewing saved recipes."""
    
    def __init__(self, parent, db_manager):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.parent = parent
        self.db_manager = db_manager
        
        self.setWindowTitle("Công thức đã lưu")
        self.setMinimumSize(QSize(500, 400))
        
        self._create_ui()
        self._load_recipes()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Danh sách công thức đã lưu")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Tìm kiếm:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Nhập tên món ăn...")
        self.filter_edit.textChanged.connect(self._filter_recipes)
        
        cuisine_label = QLabel("Phong cách:")
        self.cuisine_combo = QComboBox()
        self.cuisine_combo.addItem("Tất cả", "")
        # Cuisines will be populated in _load_recipes
        self.cuisine_combo.currentIndexChanged.connect(self._filter_recipes)
        
        # Apply consistent ComboBox styling
        self.cuisine_combo.setStyleSheet("""
            QComboBox {
                font-size: 11pt;
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                min-height: 25px;
                color: black;
                background-color: white;
            }
            QComboBox::drop-down {
                width: 30px;
                border: none;
                background-color: transparent;
            }
            QComboBox:hover {
                border: 1px solid #DB7093;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #CCCCCC;
                color: black;
                selection-background-color: #DB7093;
                selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 5px;
                border: none;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #DB7093;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #FFF0F5;
                color: black;
                border: none;
            }
        """)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(cuisine_label)
        filter_layout.addWidget(self.cuisine_combo)
        
        layout.addLayout(filter_layout)
        
        # Recipes list
        self.recipes_list = QListWidget()
        self.recipes_list.doubleClicked.connect(self._view_recipe)
        layout.addWidget(self.recipes_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        view_button = QPushButton("Xem công thức")
        view_button.clicked.connect(self._view_selected_recipe)
        
        delete_button = QPushButton("Xóa công thức")
        delete_button.clicked.connect(self._delete_recipe)
        
        close_button = QPushButton("Đóng")
        close_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(view_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def _load_recipes(self):
        """Load recipes from database."""
        recipes = self.db_manager.get_all_recipes()
        
        # Clear current list
        self.recipes_list.clear()
        
        # Collect unique cuisines
        cuisines = set()
        
        for recipe in recipes:
            # Add recipe to list
            item = QListWidgetItem(f"{recipe.name} ({recipe.cuisine_type})")
            item.setData(Qt.ItemDataRole.UserRole, recipe)
            self.recipes_list.addItem(item)
            
            # Add cuisine type to set
            if recipe.cuisine_type:
                cuisines.add(recipe.cuisine_type)
        
        # Populate cuisine filter
        current_text = self.cuisine_combo.currentText()
        self.cuisine_combo.clear()
        self.cuisine_combo.addItem("Tất cả", "")
        
        for cuisine in sorted(cuisines):
            self.cuisine_combo.addItem(cuisine, cuisine)
        
        # Try to restore previous selection
        index = self.cuisine_combo.findText(current_text)
        if index >= 0:
            self.cuisine_combo.setCurrentIndex(index)
    
    def _filter_recipes(self):
        """Filter recipes by name and cuisine."""
        filter_text = self.filter_edit.text().lower()
        cuisine = self.cuisine_combo.currentData()
        
        for i in range(self.recipes_list.count()):
            item = self.recipes_list.item(i)
            recipe = item.data(Qt.ItemDataRole.UserRole)
            
            # Check if matches filter
            name_match = filter_text in recipe.name.lower()
            cuisine_match = not cuisine or recipe.cuisine_type == cuisine
            
            # Show/hide item
            item.setHidden(not (name_match and cuisine_match))
    
    def _view_selected_recipe(self):
        """View the selected recipe."""
        selected_items = self.recipes_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "Chọn công thức",
                "Vui lòng chọn một công thức để xem."
            )
            return
        
        self._view_recipe()
    
    def _view_recipe(self):
        """View the selected recipe."""
        selected_items = self.recipes_list.selectedItems()
        if not selected_items:
            return
        
        recipe = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        try:
            recipe_data = json.loads(recipe.content)
            dialog = RecipeDialog(self, recipe_data, recipe.name)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể hiển thị công thức: {str(e)}"
            )
    
    def _delete_recipe(self):
        """Delete the selected recipe."""
        selected_items = self.recipes_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "Chọn công thức",
                "Vui lòng chọn một công thức để xóa."
            )
            return
        
        recipe = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm deletion
        confirmation = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc muốn xóa công thức '{recipe.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_recipe(recipe.id)
                self._load_recipes()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    f"Không thể xóa công thức: {str(e)}"
                )


class SavedMenusDialog(QDialog):
    """Dialog for viewing saved menus."""
    
    def __init__(self, parent, db_manager):
        """Initialize the dialog."""
        super().__init__(parent)
        
        self.parent = parent
        self.db_manager = db_manager
        self.selected_menu = None
        
        self.setWindowTitle("Thực đơn đã lưu")
        self.setMinimumSize(QSize(600, 400))
        
        self._create_ui()
        self._load_menus()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Danh sách thực đơn đã lưu")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Tìm kiếm:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Nhập tên thực đơn...")
        self.filter_edit.textChanged.connect(self._filter_menus)
        
        cuisine_label = QLabel("Phong cách:")
        self.cuisine_combo = QComboBox()
        self.cuisine_combo.addItem("Tất cả", "")
        # Cuisines will be populated in _load_menus
        self.cuisine_combo.currentIndexChanged.connect(self._filter_menus)
        
        # Apply consistent ComboBox styling
        self.cuisine_combo.setStyleSheet("""
            QComboBox {
                font-size: 11pt;
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                min-height: 25px;
                color: black;
                background-color: white;
            }
            QComboBox::drop-down {
                width: 30px;
                border: none;
                background-color: transparent;
            }
            QComboBox:hover {
                border: 1px solid #DB7093;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #CCCCCC;
                color: black;
                selection-background-color: #DB7093;
                selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 5px;
                border: none;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #DB7093;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #FFF0F5;
                color: black;
                border: none;
            }
        """)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(cuisine_label)
        filter_layout.addWidget(self.cuisine_combo)
        
        layout.addLayout(filter_layout)
        
        # Menus list
        self.menus_list = QListWidget()
        self.menus_list.doubleClicked.connect(self._load_selected_menu)
        layout.addWidget(self.menus_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        load_button = QPushButton("Tải thực đơn")
        load_button.clicked.connect(self._load_selected_menu)
        
        delete_button = QPushButton("Xóa thực đơn")
        delete_button.clicked.connect(self._delete_menu)
        
        close_button = QPushButton("Đóng")
        close_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(load_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def _load_menus(self):
        """Load menus from database."""
        try:
            menus = self.db_manager.get_all_menus()
            print(f"Loaded {len(menus)} menus from database")
            
            # Clear current list
            self.menus_list.clear()
            
            # Collect unique cuisines
            cuisines = set()
            
            for menu in menus:
                try:
                    # Debug info
                    print(f"Processing menu: id={menu.id}, name={menu.name}, meals type={type(menu.meals)}")
                    
                    # Add menu to list
                    creation_date = datetime.strptime(menu.creation_date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    item = QListWidgetItem(f"{menu.name} - {creation_date}")
                    item.setData(Qt.ItemDataRole.UserRole, menu)
                    self.menus_list.addItem(item)
                    
                    # Add cuisine type to set
                    if menu.cuisine_type:
                        cuisines.add(menu.cuisine_type)
                except Exception as e:
                    print(f"Error processing menu {menu.id}: {str(e)}")
            
            # Populate cuisine filter
            current_text = self.cuisine_combo.currentText()
            self.cuisine_combo.clear()
            self.cuisine_combo.addItem("Tất cả", "")
            
            for cuisine in sorted(cuisines):
                self.cuisine_combo.addItem(cuisine, cuisine)
            
            # Try to restore previous selection
            index = self.cuisine_combo.findText(current_text)
            if index >= 0:
                self.cuisine_combo.setCurrentIndex(index)
                
            # Add information message if no menus found
            if self.menus_list.count() == 0:
                no_items = QListWidgetItem("Không có thực đơn nào được lưu")
                no_items.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
                no_items.setForeground(QColor("gray"))
                self.menus_list.addItem(no_items)
                
        except Exception as e:
            print(f"Error loading menus: {str(e)}")
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tải danh sách thực đơn: {str(e)}"
            )
    
    def _filter_menus(self):
        """Filter menus by name and cuisine."""
        try:
            filter_text = self.filter_edit.text().lower()
            cuisine = self.cuisine_combo.currentData()
            
            # Check if we have a valid list first
            if self.menus_list.count() == 0:
                return
                
            # Check if it's just our "no items" message
            if self.menus_list.count() == 1:
                item = self.menus_list.item(0)
                if item.text() == "Không có thực đơn nào được lưu":
                    return
            
            for i in range(self.menus_list.count()):
                item = self.menus_list.item(i)
                menu = item.data(Qt.ItemDataRole.UserRole)
                
                # Skip items without data (like the "no items" message)
                if not menu:
                    continue
                
                # Check if matches filter
                name_match = filter_text in menu.name.lower()
                cuisine_match = not cuisine or menu.cuisine_type == cuisine
                
                # Show/hide item
                item.setHidden(not (name_match and cuisine_match))
        except Exception as e:
            print(f"Error filtering menus: {str(e)}")
    
    def _load_selected_menu(self):
        """Load the selected menu."""
        try:
            selected_items = self.menus_list.selectedItems()
            if not selected_items:
                QMessageBox.information(
                    self,
                    "Chọn thực đơn",
                    "Vui lòng chọn một thực đơn để tải."
                )
                return
            
            # Get the selected menu data
            item = selected_items[0]
            menu = item.data(Qt.ItemDataRole.UserRole)
            
            # Verify the menu has data
            if not menu:
                QMessageBox.critical(
                    self, 
                    "Lỗi", 
                    "Không thể tải thực đơn (dữ liệu không hợp lệ)"
                )
                return
                
            print(f"Selected menu: id={menu.id}, name={menu.name}")
            
            # Validate the meals data
            if not hasattr(menu, 'meals') or not menu.meals:
                QMessageBox.critical(
                    self, 
                    "Lỗi", 
                    "Thực đơn không có dữ liệu món ăn. Vui lòng chọn thực đơn khác."
                )
                return
                
            # Try to parse the meals JSON to make sure it's valid
            try:
                json.loads(menu.meals)
            except json.JSONDecodeError as e:
                QMessageBox.critical(
                    self, 
                    "Lỗi", 
                    f"Dữ liệu thực đơn không hợp lệ: {str(e)}"
                )
                return
            
            self.selected_menu = menu
            self.accept()
        except Exception as e:
            print(f"Error loading selected menu: {str(e)}")
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tải thực đơn đã chọn: {str(e)}"
            )
    
    def _delete_menu(self):
        """Delete the selected menu."""
        try:
            selected_items = self.menus_list.selectedItems()
            if not selected_items:
                QMessageBox.information(
                    self,
                    "Chọn thực đơn",
                    "Vui lòng chọn một thực đơn để xóa."
                )
                return
            
            # Get the menu from the item
            item = selected_items[0]
            menu = item.data(Qt.ItemDataRole.UserRole)
            
            # Verify we have a valid menu
            if not menu or not hasattr(menu, 'id'):
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    "Không thể xóa thực đơn (dữ liệu không hợp lệ)"
                )
                return
            
            # Confirm deletion
            confirmation = QMessageBox.question(
                self,
                "Xác nhận",
                f"Bạn có chắc muốn xóa thực đơn '{menu.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirmation == QMessageBox.StandardButton.Yes:
                try:
                    self.db_manager.delete_menu(menu.id)
                    print(f"Deleted menu: id={menu.id}, name={menu.name}")
                    self._load_menus()
                except Exception as e:
                    print(f"Error deleting menu {menu.id}: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Lỗi",
                        f"Không thể xóa thực đơn: {str(e)}"
                    )
        except Exception as e:
            print(f"Error in delete menu: {str(e)}")
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể xóa thực đơn: {str(e)}"
            ) 