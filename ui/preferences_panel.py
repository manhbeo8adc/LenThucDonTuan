"""
User preferences panel for the application.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QGroupBox,
    QComboBox, QSplitter, QFrame, QMessageBox, QScrollArea,
    QGridLayout, QToolButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor

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
        main_layout.setSpacing(15)  # Tăng khoảng cách giữa các phần
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - User list
        user_list_container = QWidget()
        user_list_layout = QVBoxLayout(user_list_container)
        user_list_layout.setContentsMargins(10, 10, 10, 10)
        
        user_label = QLabel("Người dùng")
        user_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #DB7093;")
        
        self.user_list = QListWidget()
        self.user_list.currentItemChanged.connect(self._on_user_selected)
        self.user_list.setMinimumWidth(200)  # Tăng chiều rộng tối thiểu
        self.user_list.setStyleSheet("""
            QListWidget {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 8px;
                padding: 5px;
                font-size: 12pt;
            }
            QListWidget::item {
                height: 35px;
                padding: 4px;
                border-bottom: 1px solid #FFD1DC;
            }
            QListWidget::item:selected {
                background-color: #DB7093;
                color: white;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #FFB6C1;
                border-radius: 4px;
            }
        """)
        
        # User actions
        user_actions_layout = QHBoxLayout()
        
        self.add_user_button = QPushButton("Thêm")
        self.add_user_button.clicked.connect(self._add_user)
        self.add_user_button.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                padding: 6px 12px;
                background-color: #DB7093;
                color: white;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #C1638A;
            }
        """)
        
        self.remove_user_button = QPushButton("Xóa")
        self.remove_user_button.clicked.connect(self._remove_user)
        self.remove_user_button.setEnabled(False)
        self.remove_user_button.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                padding: 6px 12px;
                background-color: #FFF0F5;
                color: #888888;
                border: 1px solid #FFB6C1;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover:enabled {
                background-color: #FFD1DC;
                color: #DB7093;
            }
            QPushButton:disabled {
                color: #CCCCCC;
                background-color: #F8F8F8;
                border: 1px solid #EEEEEE;
            }
        """)
        
        user_actions_layout.addWidget(self.add_user_button)
        user_actions_layout.addWidget(self.remove_user_button)
        
        user_list_layout.addWidget(user_label)
        user_list_layout.addWidget(self.user_list)
        user_list_layout.addLayout(user_actions_layout)
        
        # Right side - User preferences
        preferences_container = QWidget()
        preferences_layout = QVBoxLayout(preferences_container)
        preferences_layout.setContentsMargins(10, 10, 10, 10)
        
        preferences_label = QLabel("Sở thích")
        preferences_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #DB7093;")
        
        # User name
        name_layout = QHBoxLayout()
        name_label = QLabel("Tên:")
        name_label.setMinimumWidth(80)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập tên người dùng")
        self.name_edit.textChanged.connect(self._enable_save)
        # Make name text more stylish and feminine
        self.name_edit.setStyleSheet("""
            QLineEdit {
                font-family: 'Segoe UI', 'Arial';
                font-size: 13pt;
                font-weight: bold;
                color: #DB7093;
                padding: 8px;
                border: 1px solid #FFB6C1;
                border-radius: 6px;
                background-color: #FFF0F5;
            }
            QLineEdit:focus {
                border: 2px solid #DB7093;
            }
        """)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        
        # Scroll area để chứa tất cả các danh sách
        preferences_scroll = QScrollArea()
        preferences_scroll.setWidgetResizable(True)
        preferences_scroll.setFrameShape(QFrame.NoFrame)
        
        preferences_content = QWidget()
        preferences_scroll_layout = QVBoxLayout(preferences_content)
        preferences_scroll_layout.setSpacing(15)  # Tăng khoảng cách
        
        # Favorite ingredients
        favorites_group = QGroupBox("Nguyên liệu yêu thích")
        favorites_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #DB7093;
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 8px;
            }
        """)
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
        
        # Tạo wrapper cho grid layout
        favorites_list_wrapper = QWidget()
        favorites_grid = QGridLayout(favorites_list_wrapper)
        favorites_grid.setSpacing(5)  # Giảm khoảng cách giữa các items
        
        self.favorite_ingredients_list = CustomGridList()
        self.favorite_ingredients_list.itemSelectionChanged.connect(self._enable_save)
        
        favorites_grid.addWidget(self.favorite_ingredients_list)
        
        remove_favorite_button = QPushButton("Xóa đã chọn")
        remove_favorite_button.clicked.connect(lambda: self._remove_selected_items(self.favorite_ingredients_list))
        remove_favorite_button.setMaximumWidth(150)
        remove_favorite_button.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                padding: 5px;
                border-radius: 4px;
                background-color: #F8F8F8;
                color: #888888;
                border: 1px solid #CCCCCC;
            }
            QPushButton:hover {
                background-color: #E6E6E6;
                color: #666666;
            }
        """)
        
        favorites_layout.addLayout(favorites_input_layout)
        favorites_layout.addWidget(favorites_list_wrapper)
        favorites_layout.addWidget(remove_favorite_button)
        
        # Disliked ingredients
        dislikes_group = QGroupBox("Nguyên liệu không thích")
        dislikes_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #DB7093;
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 8px;
            }
        """)
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
        
        # Tạo wrapper cho grid layout
        dislikes_list_wrapper = QWidget()
        dislikes_grid = QGridLayout(dislikes_list_wrapper)
        dislikes_grid.setSpacing(5)  # Giảm khoảng cách giữa các items
        
        self.disliked_ingredients_list = CustomGridList()
        self.disliked_ingredients_list.itemSelectionChanged.connect(self._enable_save)
        
        dislikes_grid.addWidget(self.disliked_ingredients_list)
        
        remove_dislike_button = QPushButton("Xóa đã chọn")
        remove_dislike_button.clicked.connect(lambda: self._remove_selected_items(self.disliked_ingredients_list))
        remove_dislike_button.setMaximumWidth(150)
        remove_dislike_button.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                padding: 5px;
                border-radius: 4px;
                background-color: #F8F8F8;
                color: #888888;
                border: 1px solid #CCCCCC;
            }
            QPushButton:hover {
                background-color: #E6E6E6;
                color: #666666;
            }
        """)
        
        dislikes_layout.addLayout(dislikes_input_layout)
        dislikes_layout.addWidget(dislikes_list_wrapper)
        dislikes_layout.addWidget(remove_dislike_button)
        
        # Favorite dishes
        favorite_dishes_group = QGroupBox("Món ăn yêu thích")
        favorite_dishes_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #DB7093;
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 8px;
            }
        """)
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
        
        # Tạo wrapper cho grid layout
        favorite_dishes_list_wrapper = QWidget()
        favorite_dishes_grid = QGridLayout(favorite_dishes_list_wrapper)
        favorite_dishes_grid.setSpacing(5)  # Giảm khoảng cách giữa các items
        
        self.favorite_dishes_list = CustomGridList()
        self.favorite_dishes_list.itemSelectionChanged.connect(self._enable_save)
        
        favorite_dishes_grid.addWidget(self.favorite_dishes_list)
        
        remove_favorite_dish_button = QPushButton("Xóa đã chọn")
        remove_favorite_dish_button.clicked.connect(lambda: self._remove_selected_items(self.favorite_dishes_list))
        remove_favorite_dish_button.setMaximumWidth(150)
        remove_favorite_dish_button.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                padding: 5px;
                border-radius: 4px;
                background-color: #F8F8F8;
                color: #888888;
                border: 1px solid #CCCCCC;
            }
            QPushButton:hover {
                background-color: #E6E6E6;
                color: #666666;
            }
        """)
        
        favorite_dishes_layout.addLayout(favorite_dishes_input_layout)
        favorite_dishes_layout.addWidget(favorite_dishes_list_wrapper)
        favorite_dishes_layout.addWidget(remove_favorite_dish_button)
        
        # Disliked dishes
        disliked_dishes_group = QGroupBox("Món ăn không thích")
        disliked_dishes_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #DB7093;
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 8px;
            }
        """)
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
        
        # Tạo wrapper cho grid layout
        disliked_dishes_list_wrapper = QWidget()
        disliked_dishes_grid = QGridLayout(disliked_dishes_list_wrapper)
        disliked_dishes_grid.setSpacing(5)  # Giảm khoảng cách giữa các items
        
        self.disliked_dishes_list = CustomGridList()
        self.disliked_dishes_list.itemSelectionChanged.connect(self._enable_save)
        
        disliked_dishes_grid.addWidget(self.disliked_dishes_list)
        
        remove_disliked_dish_button = QPushButton("Xóa đã chọn")
        remove_disliked_dish_button.clicked.connect(lambda: self._remove_selected_items(self.disliked_dishes_list))
        remove_disliked_dish_button.setMaximumWidth(150)
        remove_disliked_dish_button.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                padding: 5px;
                border-radius: 4px;
                background-color: #F8F8F8;
                color: #888888;
                border: 1px solid #CCCCCC;
            }
            QPushButton:hover {
                background-color: #E6E6E6;
                color: #666666;
            }
        """)
        
        disliked_dishes_layout.addLayout(disliked_dishes_input_layout)
        disliked_dishes_layout.addWidget(disliked_dishes_list_wrapper)
        disliked_dishes_layout.addWidget(remove_disliked_dish_button)
        
        # Add all groups to preferences scroll layout
        preferences_scroll_layout.addWidget(favorites_group)
        preferences_scroll_layout.addWidget(dislikes_group)
        preferences_scroll_layout.addWidget(favorite_dishes_group)
        preferences_scroll_layout.addWidget(disliked_dishes_group)
        
        # Set the scroll content
        preferences_scroll.setWidget(preferences_content)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Lưu thay đổi")
        self.save_button.clicked.connect(self._save_user)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 8px 15px;
                background-color: #DB7093;
                color: white;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover:enabled {
                background-color: #C1638A;
            }
            QPushButton:disabled {
                background-color: #F8F8F8;
                color: #CCCCCC;
                border: 1px solid #EEEEEE;
            }
        """)
        
        self.select_button = QPushButton("Sử dụng người dùng này")
        self.select_button.clicked.connect(self._select_user)
        self.select_button.setEnabled(False)
        self.select_button.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 8px 15px;
                background-color: #FFF0F5;
                color: #DB7093;
                border: 1px solid #FFB6C1;
                border-radius: 6px;
                min-width: 180px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #FFD1DC;
            }
            QPushButton:disabled {
                background-color: #F8F8F8;
                color: #CCCCCC;
                border: 1px solid #EEEEEE;
            }
        """)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.select_button)
        
        # Add all to preferences layout
        preferences_layout.addWidget(preferences_label)
        preferences_layout.addLayout(name_layout)
        preferences_layout.addWidget(preferences_scroll)
        preferences_layout.addLayout(actions_layout)
        
        # Add panels to splitter
        splitter.addWidget(user_list_container)
        splitter.addWidget(preferences_container)
        
        # Set initial sizes
        splitter.setSizes([1, 3])  # Preferences panel gets more space
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Disable preferences editing initially
        self._enable_preferences_editing(False)
    
    def _load_users(self):
        """Load users from database."""
        users = self.db_manager.get_all_users()
        
        # Clear current list
        self.user_list.clear()
        
        # Add users to list
        for user in users:
            item = QListWidgetItem(user.name)
            item.setData(Qt.ItemDataRole.UserRole, user)
            self.user_list.addItem(item)
    
    def _on_user_selected(self, current, previous):
        """Handle user selection."""
        if current:
            # Get user from item
            self.current_user = current.data(Qt.ItemDataRole.UserRole)
            
            # Enable editing
            self._enable_preferences_editing(True)
            
            # Populate preferences
            self._populate_user_preferences()
            
            # Enable remove button
            self.remove_user_button.setEnabled(True)
            
            # Enable select button
            self.select_button.setEnabled(True)
        else:
            self._enable_preferences_editing(False)
            self.remove_user_button.setEnabled(False)
            self.select_button.setEnabled(False)
    
    def _populate_user_preferences(self):
        """Populate preferences with user data."""
        if not self.current_user:
            return
        
        # Set name
        self.name_edit.setText(self.current_user.name)
        
        # Clear lists
        self.favorite_ingredients_list.clear()
        self.disliked_ingredients_list.clear()
        self.favorite_dishes_list.clear()
        self.disliked_dishes_list.clear()
        
        # Populate lists
        for ingredient in self.current_user.favorite_ingredients:
            self.favorite_ingredients_list.addItem(ingredient)
        
        for ingredient in self.current_user.disliked_ingredients:
            self.disliked_ingredients_list.addItem(ingredient)
        
        for dish in self.current_user.favorite_dishes:
            self.favorite_dishes_list.addItem(dish)
        
        for dish in self.current_user.disliked_dishes:
            self.disliked_dishes_list.addItem(dish)
    
    def _enable_preferences_editing(self, enabled):
        """Enable or disable preferences editing."""
        self.name_edit.setEnabled(enabled)
        self.favorite_ingredient_edit.setEnabled(enabled)
        self.disliked_ingredient_edit.setEnabled(enabled)
        self.favorite_dish_edit.setEnabled(enabled)
        self.disliked_dish_edit.setEnabled(enabled)
        
        self.add_favorite_button.setEnabled(enabled)
        self.add_dislike_button.setEnabled(enabled)
        self.add_favorite_dish_button.setEnabled(enabled)
        self.add_disliked_dish_button.setEnabled(enabled)
        
        self.favorite_ingredients_list.setEnabled(enabled)
        self.disliked_ingredients_list.setEnabled(enabled)
        self.favorite_dishes_list.setEnabled(enabled)
        self.disliked_dishes_list.setEnabled(enabled)
        
        self.save_button.setEnabled(enabled and self._has_changes())
    
    def _add_user(self):
        """Add a new user."""
        self.current_user = User(name="Người dùng mới")
        
        # Add to list
        item = QListWidgetItem(self.current_user.name)
        item.setData(Qt.ItemDataRole.UserRole, self.current_user)
        self.user_list.addItem(item)
        self.user_list.setCurrentItem(item)
        
        # Enable editing
        self._enable_preferences_editing(True)
        
        # Populate preferences
        self._populate_user_preferences()
    
    def _remove_user(self):
        """Remove the selected user."""
        if not self.current_user:
            return
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc muốn xóa người dùng '{self.current_user.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Remove from database
            if self.current_user.id:
                self.db_manager.delete_user(self.current_user.id)
            
            # Remove from list
            row = self.user_list.currentRow()
            self.user_list.takeItem(row)
            
            # Clear current user
            self.current_user = None
            
            # Disable editing
            self._enable_preferences_editing(False)
    
    def _add_item_to_list(self, line_edit, list_widget):
        """Add item to list from line edit."""
        text = line_edit.text().strip()
        if text:
            # Check if already exists
            items = list_widget.findItems(text, Qt.MatchFlag.MatchExactly)
            if not items:
                list_widget.addItem(text)
                self._enable_save()
            else:
                QMessageBox.information(
                    self,
                    "Đã tồn tại",
                    f"'{text}' đã có trong danh sách."
                )
            
            # Clear line edit
            line_edit.clear()
            line_edit.setFocus()
    
    def _remove_selected_items(self, list_widget):
        """Remove selected items from list."""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = list_widget.row(item)
            list_widget.takeItem(row)
        
        self._enable_save()
    
    def _save_user(self):
        """Save user preferences."""
        if not self.current_user:
            return
        
        # Update name
        self.current_user.name = self.name_edit.text()
        
        # Update lists
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
        
        # Update list item
        item = self.user_list.currentItem()
        if item:
            item.setText(self.current_user.name)
            item.setData(Qt.ItemDataRole.UserRole, self.current_user)
        
        # Disable save button
        self.save_button.setEnabled(False)
    
    def _select_user(self):
        """Select user and emit signal."""
        if self.current_user:
            self.user_selected.emit(self.current_user)
            
            # Get the main window (parent of parent) to show toast notification
            main_window = self.window()
            if hasattr(main_window, 'show_toast'):
                main_window.show_toast(f"Đã chọn người dùng: {self.current_user.name}")
    
    def _enable_save(self):
        """Enable save button if changes are made."""
        self.save_button.setEnabled(self._has_changes())
    
    def _has_changes(self):
        """Check if there are unsaved changes."""
        if not self.current_user:
            return False
        
        # Check name
        if self.current_user.name != self.name_edit.text():
            return True
        
        # Check lists
        current_favorites = set(self.current_user.favorite_ingredients)
        new_favorites = {self.favorite_ingredients_list.item(i).text() for i in range(self.favorite_ingredients_list.count())}
        
        current_dislikes = set(self.current_user.disliked_ingredients)
        new_dislikes = {self.disliked_ingredients_list.item(i).text() for i in range(self.disliked_ingredients_list.count())}
        
        current_favorite_dishes = set(self.current_user.favorite_dishes)
        new_favorite_dishes = {self.favorite_dishes_list.item(i).text() for i in range(self.favorite_dishes_list.count())}
        
        current_disliked_dishes = set(self.current_user.disliked_dishes)
        new_disliked_dishes = {self.disliked_dishes_list.item(i).text() for i in range(self.disliked_dishes_list.count())}
        
        return (current_favorites != new_favorites or
                current_dislikes != new_dislikes or
                current_favorite_dishes != new_favorite_dishes or
                current_disliked_dishes != new_disliked_dishes)


class CustomGridList(QListWidget):
    """Custom list widget that shows items in a grid-like format."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setWrapping(True)
        self.setSpacing(8)
        self.setMinimumHeight(120)  # Tăng chiều cao tối thiểu
        self.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
            }
            QListWidget::item {
                background-color: #F0F8FF;
                border: 1px solid #ADD8E6;
                border-radius: 6px;
                padding: 8px;
                margin: 4px;
                min-width: 90px;
                max-width: 150px;
                min-height: 25px;
            }
            QListWidget::item:selected {
                background-color: #DB7093;
                color: white;
                border: 1px solid #C25B7A;
            }
            QListWidget::item:hover {
                background-color: #E6E6FA;
                border: 1px solid #B0C4DE;
            }
        """)
    
    def addItem(self, text):
        """Override addItem to create custom item appearance."""
        item = QListWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        super().addItem(item) 