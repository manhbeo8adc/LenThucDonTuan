"""
Budget and preparation time panel for the application.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider, QComboBox, QSpinBox, QCheckBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal

from config import BUDGET_OPTIONS, PREP_TIME_OPTIONS, DAYS_OF_WEEK, MEALS_PER_DAY
from utils.helpers import format_currency, format_time


class BudgetPanel(QWidget):
    """Panel for setting budget and preparation time."""
    
    # Signal emitted when budget settings are changed
    budget_settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the panel."""
        super().__init__()
        
        self.settings = {
            "budget_per_meal": 70000,
            "max_prep_time": 60,
            "days": DAYS_OF_WEEK.copy(),
            "meals_per_day": MEALS_PER_DAY.copy(),
            "servings": 4  # Default servings
        }
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Ngân sách và Thời gian chuẩn bị")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #DB7093;")
        main_layout.addWidget(title_label)
        
        # Description
        description_label = QLabel(
            "Thiết lập ngân sách cho mỗi bữa ăn, thời gian tối đa bạn muốn dành cho việc chuẩn bị và số người ăn. "
            "Đồng thời, chọn các ngày và bữa ăn bạn muốn tạo thực đơn."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 11pt; margin-bottom: 10px;")
        main_layout.addWidget(description_label)
        
        # Common QGroupBox style
        group_box_style = """
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #DB7093;
            }
        """
        
        # Budget settings
        budget_group = QGroupBox("Ngân sách")
        budget_group.setStyleSheet(group_box_style)
        budget_layout = QVBoxLayout(budget_group)
        
        # Budget slider
        budget_slider_layout = QHBoxLayout()
        budget_slider_label = QLabel("Ngân sách mỗi bữa:")
        budget_slider_label.setMinimumWidth(150)
        self.budget_slider = QSlider(Qt.Orientation.Horizontal)
        self.budget_slider.setMinimum(30000)
        self.budget_slider.setMaximum(300000)
        self.budget_slider.setTickInterval(10000)
        self.budget_slider.setSingleStep(10000)
        self.budget_slider.setValue(self.settings["budget_per_meal"])
        self.budget_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.budget_value_label = QLabel(format_currency(self.settings["budget_per_meal"]))
        self.budget_value_label.setMinimumWidth(100)
        self.budget_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.budget_value_label.setStyleSheet("font-weight: bold; color: #DB7093;")
        
        self.budget_slider.valueChanged.connect(self._on_budget_changed)
        
        budget_slider_layout.addWidget(budget_slider_label)
        budget_slider_layout.addWidget(self.budget_slider)
        budget_slider_layout.addWidget(self.budget_value_label)
        
        # Budget presets
        budget_presets_layout = QHBoxLayout()
        budget_presets_label = QLabel("Hoặc chọn:")
        budget_presets_label.setMinimumWidth(150)
        self.budget_presets = QComboBox()
        
        for budget in BUDGET_OPTIONS:
            self.budget_presets.addItem(format_currency(int(budget)), int(budget))
        
        self.budget_presets.currentIndexChanged.connect(self._on_budget_preset_changed)
        
        budget_presets_layout.addWidget(budget_presets_label)
        budget_presets_layout.addWidget(self.budget_presets)
        budget_presets_layout.addStretch()
        
        # Add common ComboBox styling to fix hover issues
        combobox_style = """
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
        """
        
        # Apply the style to all combo boxes
        self.budget_presets.setStyleSheet(combobox_style)
        
        budget_layout.addLayout(budget_slider_layout)
        budget_layout.addLayout(budget_presets_layout)
        
        # Prep time settings
        prep_time_group = QGroupBox("Thời gian chuẩn bị")
        prep_time_group.setStyleSheet(group_box_style)
        prep_time_layout = QVBoxLayout(prep_time_group)
        
        # Prep time slider
        prep_time_slider_layout = QHBoxLayout()
        prep_time_slider_label = QLabel("Thời gian tối đa:")
        prep_time_slider_label.setMinimumWidth(150)
        self.prep_time_slider = QSlider(Qt.Orientation.Horizontal)
        self.prep_time_slider.setMinimum(15)
        self.prep_time_slider.setMaximum(180)
        self.prep_time_slider.setTickInterval(15)
        self.prep_time_slider.setSingleStep(15)
        self.prep_time_slider.setValue(self.settings["max_prep_time"])
        self.prep_time_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.prep_time_value_label = QLabel(format_time(self.settings["max_prep_time"]))
        self.prep_time_value_label.setMinimumWidth(100)
        self.prep_time_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.prep_time_value_label.setStyleSheet("font-weight: bold; color: #DB7093;")
        
        self.prep_time_slider.valueChanged.connect(self._on_prep_time_changed)
        
        prep_time_slider_layout.addWidget(prep_time_slider_label)
        prep_time_slider_layout.addWidget(self.prep_time_slider)
        prep_time_slider_layout.addWidget(self.prep_time_value_label)
        
        # Prep time presets
        prep_time_presets_layout = QHBoxLayout()
        prep_time_presets_label = QLabel("Hoặc chọn:")
        prep_time_presets_label.setMinimumWidth(150)
        self.prep_time_presets = QComboBox()
        
        for time in PREP_TIME_OPTIONS:
            self.prep_time_presets.addItem(format_time(int(time)), int(time))
        
        self.prep_time_presets.currentIndexChanged.connect(self._on_prep_time_preset_changed)
        
        prep_time_presets_layout.addWidget(prep_time_presets_label)
        prep_time_presets_layout.addWidget(self.prep_time_presets)
        prep_time_presets_layout.addStretch()
        
        # Add common ComboBox styling to fix hover issues
        self.prep_time_presets.setStyleSheet(combobox_style)
        
        prep_time_layout.addLayout(prep_time_slider_layout)
        prep_time_layout.addLayout(prep_time_presets_layout)
        
        # THÊM MỚI: Servings settings
        servings_group = QGroupBox("Khẩu phần ăn")
        servings_group.setStyleSheet(group_box_style)
        servings_layout = QVBoxLayout(servings_group)
        
        servings_input_layout = QHBoxLayout()
        servings_label = QLabel("Số người ăn:")
        servings_label.setMinimumWidth(150)
        
        self.servings_spin = QSpinBox()
        self.servings_spin.setMinimum(1)
        self.servings_spin.setMaximum(20)
        self.servings_spin.setValue(self.settings["servings"])
        self.servings_spin.valueChanged.connect(self._on_servings_changed)
        
        servings_description = QLabel("người")
        servings_description.setMinimumWidth(100)
        servings_description.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        servings_input_layout.addWidget(servings_label)
        servings_input_layout.addWidget(self.servings_spin)
        servings_input_layout.addWidget(servings_description)
        servings_input_layout.addStretch()
        
        servings_hint_label = QLabel("* Số người ăn giúp tính toán khẩu phần và nguyên liệu chính xác hơn")
        servings_hint_label.setStyleSheet("font-style: italic; color: #888888; font-size: 10pt;")
        
        servings_layout.addLayout(servings_input_layout)
        servings_layout.addWidget(servings_hint_label)
        
        # Days and Meals layout using two separate horizontal sections
        days_section = QVBoxLayout()
        meals_section = QVBoxLayout()
        
        # Days selection - using horizontal layout
        days_group = QGroupBox("Các ngày trong tuần")
        days_group.setStyleSheet(group_box_style)
        days_flow = QHBoxLayout(days_group)
        days_flow.setSpacing(10)  # Spacing between items
        days_flow.setContentsMargins(15, 25, 15, 15)  # Left, top, right, bottom margins
        
        # Create checkboxes for days in a horizontal layout
        self.day_checkboxes = {}
        
        for day in DAYS_OF_WEEK:
            checkbox = QCheckBox(day)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._on_days_changed)
            checkbox.setFixedWidth(100)  # Use fixed width
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 11pt;
                    padding: 4px;
                    spacing: 8px; /* Space between checkbox and text */
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            days_flow.addWidget(checkbox)
            self.day_checkboxes[day] = checkbox
        
        days_flow.addStretch(1)  # Add stretch at the end
        
        # Meals selection - horizontal layout
        meals_group = QGroupBox("Các bữa ăn")
        meals_group.setStyleSheet(group_box_style)
        meals_flow = QHBoxLayout(meals_group)
        meals_flow.setSpacing(20)  # More spacing between meal checkboxes
        meals_flow.setContentsMargins(15, 25, 15, 15)  # Add some padding
        
        # Create checkboxes for meals
        self.meal_checkboxes = {}
        
        for meal in MEALS_PER_DAY:
            checkbox = QCheckBox(meal)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._on_meals_changed)
            checkbox.setFixedWidth(100)  # Use fixed width
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 11pt;
                    padding: 4px;
                    spacing: 8px; /* Space between checkbox and text */
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            meals_flow.addWidget(checkbox)
            self.meal_checkboxes[meal] = checkbox
        
        meals_flow.addStretch(1)  # Add stretch at the end
        
        # Add groups to vertical layouts
        days_section.addWidget(days_group)
        meals_section.addWidget(meals_group)
        
        # Apply button with completely new styling and layout approach
        button_container = QWidget()
        button_container.setFixedHeight(60)  # Fixed height container
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        self.apply_button = QPushButton("Áp dụng thiết lập")
        self.apply_button.setFixedSize(200, 45)  # Fixed size instead of minimum size
        self.apply_button.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
                background-color: #DB7093;
                color: white;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #C1638A;
            }
            QPushButton:pressed {
                background-color: #A5547B;
            }
        """)
        self.apply_button.clicked.connect(self._apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch()
        
        # Add all components to main layout
        main_layout.addWidget(budget_group)
        main_layout.addWidget(prep_time_group)
        main_layout.addWidget(servings_group)  # Add the new servings group
        main_layout.addLayout(days_section)
        main_layout.addLayout(meals_section)
        main_layout.addWidget(button_container)  # Use the container instead of just the layout
        main_layout.addStretch()
    
    def _on_budget_changed(self, value):
        """Handle budget slider value change."""
        self.settings["budget_per_meal"] = value
        self.budget_value_label.setText(format_currency(value))
        
        # Update combo box if an exact match exists
        for i in range(self.budget_presets.count()):
            if self.budget_presets.itemData(i) == value:
                self.budget_presets.setCurrentIndex(i)
                break
    
    def _on_budget_preset_changed(self, index):
        """Handle budget preset selection."""
        if index >= 0:
            value = self.budget_presets.itemData(index)
            self.settings["budget_per_meal"] = value
            self.budget_slider.setValue(value)
            self.budget_value_label.setText(format_currency(value))
    
    def _on_prep_time_changed(self, value):
        """Handle prep time slider value change."""
        self.settings["max_prep_time"] = value
        self.prep_time_value_label.setText(format_time(value))
        
        # Update combo box if an exact match exists
        for i in range(self.prep_time_presets.count()):
            if self.prep_time_presets.itemData(i) == value:
                self.prep_time_presets.setCurrentIndex(i)
                break
    
    def _on_prep_time_preset_changed(self, index):
        """Handle prep time preset selection."""
        if index >= 0:
            value = self.prep_time_presets.itemData(index)
            self.settings["max_prep_time"] = value
            self.prep_time_slider.setValue(value)
            self.prep_time_value_label.setText(format_time(value))
    
    def _on_servings_changed(self, value):
        """Handle servings value change."""
        self.settings["servings"] = value
    
    def _on_days_changed(self):
        """Handle days checkboxes changes."""
        self.settings["days"] = [
            day for day, checkbox in self.day_checkboxes.items()
            if checkbox.isChecked()
        ]
    
    def _on_meals_changed(self):
        """Handle meals checkboxes changes."""
        self.settings["meals_per_day"] = [
            meal for meal, checkbox in self.meal_checkboxes.items()
            if checkbox.isChecked()
        ]
    
    def _apply_settings(self):
        """Apply the settings and emit the change signal."""
        # Validate settings
        if not self.settings["days"]:
            # No days selected, select all by default
            for checkbox in self.day_checkboxes.values():
                checkbox.setChecked(True)
            self.settings["days"] = DAYS_OF_WEEK.copy()
        
        if not self.settings["meals_per_day"]:
            # No meals selected, select all by default
            for checkbox in self.meal_checkboxes.values():
                checkbox.setChecked(True)
            self.settings["meals_per_day"] = MEALS_PER_DAY.copy()
        
        # Emit signal with current settings
        self.budget_settings_changed.emit(self.settings)
        
        # Get the main window to show toast notification
        main_window = self.window()
        if hasattr(main_window, 'show_toast'):
            main_window.show_toast(f"Đã áp dụng thiết lập ngân sách") 