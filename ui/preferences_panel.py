"""
User preferences panel for the application.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QGroupBox,
    QComboBox, QSplitter, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from database.models import User


class PreferencesPanel(QWidget):
    """Panel for managing user preferences."""
    
    # Signal emitted when a user is selected
    user_selected = pyqtSignal(User)
    
    def __init__(self, db_manager):
        """Initialize the panel."""
        super().__init__()
        
        self.db_manager = db_manager
        self.current_user = None
        
        self._create_ui()
        self._load_users()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QHBoxLayout(self)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - User list
        user_list_container = QWidget()
        user_list_layout = QVBoxLayout(user_list_container)
        
        user_label = QLabel("Người dùng")
        user_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.user_list = QListWidget()
        self.user_list.currentItemChanged.connect(self._on_user_selected)
        
        # User actions
        user_actions_layout = QHBoxLayout()
        
        self.add_user_button = QPushButton("Thêm")
        self.add_user_button.clicked.connect(self._add_user)
        
        self.remove_user_button = QPushButton("Xóa")
        self.remove_user_button.clicked.connect(self._remove_user)
        self.remove_user_button.setEnabled(False)
        
        user_actions_layout.addWidget(self.add_user_button)
        user_actions_layout.addWidget(self.remove_user_button)
        
        user_list_layout.addWidget(user_label)
        user_list_layout.addWidget(self.user_list)
        user_list_layout.addLayout(user_actions_layout)
        
        # Right side - User preferences
        preferences_container = QWidget()
        preferences_layout = QVBoxLayout(preferences_container)
        
        preferences_label = QLabel("Sở thích")
        preferences_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # User name
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập tên người dùng")
        self.name_edit.textChanged.connect(self._enable_save)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        
        # Favorite ingredients
        favorites_group = QGroupBox("Nguyên liệu yêu thích")
        favorites_layout = QVBoxLayout(favorites_group)
        
        favorites_input_layout = QHBoxLayout()
        self.favorite_ingredient_edit = QLineEdit()
        self.favorite_ingredient_edit.setPlaceholderText("Nhập nguyên liệu yêu thích")
        
        self.add_favorite_button = QPushButton("Thêm")
        self.add_favorite_button.clicked.connect(lambda: self._add_item_to_list(
            self.favorite_ingredient_edit, self.favorite_ingredients_list
        ))
        
        favorites_input_layout.addWidget(self.favorite_ingredient_edit)
        favorites_input_layout.addWidget(self.add_favorite_button)
        
        self.favorite_ingredients_list = QListWidget()
        self.favorite_ingredients_list.itemSelectionChanged.connect(self._enable_save)
        
        remove_favorite_button = QPushButton("Xóa đã chọn")
        remove_favorite_button.clicked.connect(lambda: self._remove_selected_items(self.favorite_ingredients_list))
        
        favorites_layout.addLayout(favorites_input_layout)
        favorites_layout.addWidget(self.favorite_ingredients_list)
        favorites_layout.addWidget(remove_favorite_button)
        
        # Disliked ingredients
        dislikes_group = QGroupBox("Nguyên liệu không thích")
        dislikes_layout = QVBoxLayout(dislikes_group)
        
        dislikes_input_layout = QHBoxLayout()
        self.disliked_ingredient_edit = QLineEdit()
        self.disliked_ingredient_edit.setPlaceholderText("Nhập nguyên liệu không thích")
        
        self.add_dislike_button = QPushButton("Thêm")
        self.add_dislike_button.clicked.connect(lambda: self._add_item_to_list(
            self.disliked_ingredient_edit, self.disliked_ingredients_list
        ))
        
        dislikes_input_layout.addWidget(self.disliked_ingredient_edit)
        dislikes_input_layout.addWidget(self.add_dislike_button)
        
        self.disliked_ingredients_list = QListWidget()
        self.disliked_ingredients_list.itemSelectionChanged.connect(self._enable_save)
        
        remove_dislike_button = QPushButton("Xóa đã chọn")
        remove_dislike_button.clicked.connect(lambda: self._remove_selected_items(self.disliked_ingredients_list))
        
        dislikes_layout.addLayout(dislikes_input_layout)
        dislikes_layout.addWidget(self.disliked_ingredients_list)
        dislikes_layout.addWidget(remove_dislike_button)
        
        # Favorite dishes
        favorite_dishes_group = QGroupBox("Món ăn yêu thích")
        favorite_dishes_layout = QVBoxLayout(favorite_dishes_group)
        
        favorite_dishes_input_layout = QHBoxLayout()
        self.favorite_dish_edit = QLineEdit()
        self.favorite_dish_edit.setPlaceholderText("Nhập món ăn yêu thích")
        
        self.add_favorite_dish_button = QPushButton("Thêm")
        self.add_favorite_dish_button.clicked.connect(lambda: self._add_item_to_list(
            self.favorite_dish_edit, self.favorite_dishes_list
        ))
        
        favorite_dishes_input_layout.addWidget(self.favorite_dish_edit)
        favorite_dishes_input_layout.addWidget(self.add_favorite_dish_button)
        
        self.favorite_dishes_list = QListWidget()
        self.favorite_dishes_list.itemSelectionChanged.connect(self._enable_save)
        
        remove_favorite_dish_button = QPushButton("Xóa đã chọn")
        remove_favorite_dish_button.clicked.connect(lambda: self._remove_selected_items(self.favorite_dishes_list))
        
        favorite_dishes_layout.addLayout(favorite_dishes_input_layout)
        favorite_dishes_layout.addWidget(self.favorite_dishes_list)
        favorite_dishes_layout.addWidget(remove_favorite_dish_button)
        
        # Disliked dishes
        disliked_dishes_group = QGroupBox("Món ăn không thích")
        disliked_dishes_layout = QVBoxLayout(disliked_dishes_group)
        
        disliked_dishes_input_layout = QHBoxLayout()
        self.disliked_dish_edit = QLineEdit()
        self.disliked_dish_edit.setPlaceholderText("Nhập món ăn không thích")
        
        self.add_disliked_dish_button = QPushButton("Thêm")
        self.add_disliked_dish_button.clicked.connect(lambda: self._add_item_to_list(
            self.disliked_dish_edit, self.disliked_dishes_list
        ))
        
        disliked_dishes_input_layout.addWidget(self.disliked_dish_edit)
        disliked_dishes_input_layout.addWidget(self.add_disliked_dish_button)
        
        self.disliked_dishes_list = QListWidget()
        self.disliked_dishes_list.itemSelectionChanged.connect(self._enable_save)
        
        remove_disliked_dish_button = QPushButton("Xóa đã chọn")
        remove_disliked_dish_button.clicked.connect(lambda: self._remove_selected_items(self.disliked_dishes_list))
        
        disliked_dishes_layout.addLayout(disliked_dishes_input_layout)
        disliked_dishes_layout.addWidget(self.disliked_dishes_list)
        disliked_dishes_layout.addWidget(remove_disliked_dish_button)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Lưu thay đổi")
        self.save_button.clicked.connect(self._save_user)
        self.save_button.setEnabled(False)
        
        self.select_button = QPushButton("Sử dụng người dùng này")
        self.select_button.clicked.connect(self._select_user)
        self.select_button.setEnabled(False)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.select_button)
        
        # Add all widgets to preferences layout
        preferences_layout.addWidget(preferences_label)
        preferences_layout.addLayout(name_layout)
        preferences_layout.addWidget(favorites_group)
        preferences_layout.addWidget(dislikes_group)
        preferences_layout.addWidget(favorite_dishes_group)
        preferences_layout.addWidget(disliked_dishes_group)
        preferences_layout.addLayout(actions_layout)
        
        # Add containers to splitter
        splitter.addWidget(user_list_container)
        splitter.addWidget(preferences_container)
        
        # Set initial sizes
        splitter.setSizes([300, 700])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Disable preferences editing initially
        self._enable_preferences_editing(False)
    
    def _load_users(self):
        """Load users from the database."""
        self.user_list.clear()
        
        users = self.db_manager.get_all_users()
        
        for user in users:
            item = QListWidgetItem(user.name)
            item.setData(Qt.ItemDataRole.UserRole, user.id)
            self.user_list.addItem(item)
    
    def _on_user_selected(self, current, previous):
        """Handle user selection."""
        if current is None:
            self._enable_preferences_editing(False)
            self.remove_user_button.setEnabled(False)
            self.current_user = None
            return
        
        user_id = current.data(Qt.ItemDataRole.UserRole)
        self.current_user = self.db_manager.get_user(user_id)
        
        if self.current_user:
            self._populate_user_preferences()
            self._enable_preferences_editing(True)
            self.remove_user_button.setEnabled(True)
            self.select_button.setEnabled(True)
    
    def _populate_user_preferences(self):
        """Populate UI with user preferences."""
        if not self.current_user:
            return
        
        # Clear previous data
        self.name_edit.setText(self.current_user.name)
        
        self.favorite_ingredients_list.clear()
        for ingredient in self.current_user.favorite_ingredients:
            self.favorite_ingredients_list.addItem(ingredient)
        
        self.disliked_ingredients_list.clear()
        for ingredient in self.current_user.disliked_ingredients:
            self.disliked_ingredients_list.addItem(ingredient)
        
        self.favorite_dishes_list.clear()
        for dish in self.current_user.favorite_dishes:
            self.favorite_dishes_list.addItem(dish)
        
        self.disliked_dishes_list.clear()
        for dish in self.current_user.disliked_dishes:
            self.disliked_dishes_list.addItem(dish)
        
        self.save_button.setEnabled(False)
    
    def _enable_preferences_editing(self, enabled):
        """Enable or disable preferences editing."""
        self.name_edit.setEnabled(enabled)
        self.favorite_ingredient_edit.setEnabled(enabled)
        self.add_favorite_button.setEnabled(enabled)
        self.favorite_ingredients_list.setEnabled(enabled)
        self.disliked_ingredient_edit.setEnabled(enabled)
        self.add_dislike_button.setEnabled(enabled)
        self.disliked_ingredients_list.setEnabled(enabled)
        self.favorite_dish_edit.setEnabled(enabled)
        self.add_favorite_dish_button.setEnabled(enabled)
        self.favorite_dishes_list.setEnabled(enabled)
        self.disliked_dish_edit.setEnabled(enabled)
        self.add_disliked_dish_button.setEnabled(enabled)
        self.disliked_dishes_list.setEnabled(enabled)
        self.save_button.setEnabled(enabled and self._has_changes())
        self.select_button.setEnabled(enabled)
    
    def _add_user(self):
        """Add a new user."""
        new_user = User(name="Người dùng mới")
        new_user = self.db_manager.save_user(new_user)
        
        if new_user:
            item = QListWidgetItem(new_user.name)
            item.setData(Qt.ItemDataRole.UserRole, new_user.id)
            self.user_list.addItem(item)
            self.user_list.setCurrentItem(item)
    
    def _remove_user(self):
        """Remove the selected user."""
        if not self.current_user:
            return
        
        confirmation = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc muốn xóa người dùng '{self.current_user.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            success = self.db_manager.delete_user(self.current_user.id)
            
            if success:
                row = self.user_list.currentRow()
                self.user_list.takeItem(row)
                self.current_user = None
                self._enable_preferences_editing(False)
                self.remove_user_button.setEnabled(False)
    
    def _add_item_to_list(self, line_edit, list_widget):
        """Add an item to a list widget."""
        text = line_edit.text().strip()
        
        if text:
            # Check if the item already exists
            for i in range(list_widget.count()):
                if list_widget.item(i).text().lower() == text.lower():
                    return
            
            list_widget.addItem(text)
            line_edit.clear()
            self._enable_save()
    
    def _remove_selected_items(self, list_widget):
        """Remove selected items from a list widget."""
        selected_items = list_widget.selectedItems()
        
        if not selected_items:
            return
        
        for item in selected_items:
            row = list_widget.row(item)
            list_widget.takeItem(row)
        
        self._enable_save()
    
    def _save_user(self):
        """Save the current user's preferences."""
        if not self.current_user:
            return
        
        # Update user data
        self.current_user.name = self.name_edit.text()
        
        self.current_user.favorite_ingredients = [
            self.favorite_ingredients_list.item(i).text()
            for i in range(self.favorite_ingredients_list.count())
        ]
        
        self.current_user.disliked_ingredients = [
            self.disliked_ingredients_list.item(i).text()
            for i in range(self.disliked_ingredients_list.count())
        ]
        
        self.current_user.favorite_dishes = [
            self.favorite_dishes_list.item(i).text()
            for i in range(self.favorite_dishes_list.count())
        ]
        
        self.current_user.disliked_dishes = [
            self.disliked_dishes_list.item(i).text()
            for i in range(self.disliked_dishes_list.count())
        ]
        
        # Save to database
        self.current_user = self.db_manager.save_user(self.current_user)
        
        # Update user list
        current_item = self.user_list.currentItem()
        if current_item:
            current_item.setText(self.current_user.name)
        
        self.save_button.setEnabled(False)
    
    def _select_user(self):
        """Emit signal to indicate the current user is selected."""
        if self.current_user:
            self.user_selected.emit(self.current_user)
    
    def _enable_save(self):
        """Enable the save button if there are changes."""
        if self.current_user:
            self.save_button.setEnabled(self._has_changes())
    
    def _has_changes(self):
        """Check if there are changes to the user preferences."""
        if not self.current_user:
            return False
        
        # Check name change
        if self.current_user.name != self.name_edit.text():
            return True
        
        # Check favorite ingredients changes
        current_favorites = set(self.current_user.favorite_ingredients)
        ui_favorites = {self.favorite_ingredients_list.item(i).text()
                       for i in range(self.favorite_ingredients_list.count())}
        
        if current_favorites != ui_favorites:
            return True
        
        # Check disliked ingredients changes
        current_dislikes = set(self.current_user.disliked_ingredients)
        ui_dislikes = {self.disliked_ingredients_list.item(i).text()
                      for i in range(self.disliked_ingredients_list.count())}
        
        if current_dislikes != ui_dislikes:
            return True
        
        # Check favorite dishes changes
        current_favorite_dishes = set(self.current_user.favorite_dishes)
        ui_favorite_dishes = {self.favorite_dishes_list.item(i).text()
                             for i in range(self.favorite_dishes_list.count())}
        
        if current_favorite_dishes != ui_favorite_dishes:
            return True
        
        # Check disliked dishes changes
        current_disliked_dishes = set(self.current_user.disliked_dishes)
        ui_disliked_dishes = {self.disliked_dishes_list.item(i).text()
                             for i in range(self.disliked_dishes_list.count())}
        
        if current_disliked_dishes != ui_disliked_dishes:
            return True
        
        return False 