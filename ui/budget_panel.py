"""
Budget and preparation time panel for the application.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider, QComboBox, QSpinBox, QCheckBox
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
            "meals_per_day": MEALS_PER_DAY.copy()
        }
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Ngân sách và Thời gian chuẩn bị")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Description
        description_label = QLabel(
            "Thiết lập ngân sách cho mỗi bữa ăn và thời gian tối đa bạn muốn dành cho việc chuẩn bị. "
            "Đồng thời, chọn các ngày và bữa ăn bạn muốn tạo thực đơn."
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)
        
        # Budget settings
        budget_group = QGroupBox("Ngân sách")
        budget_layout = QVBoxLayout(budget_group)
        
        # Budget slider
        budget_slider_layout = QHBoxLayout()
        budget_slider_label = QLabel("Ngân sách mỗi bữa:")
        self.budget_slider = QSlider(Qt.Orientation.Horizontal)
        self.budget_slider.setMinimum(30000)
        self.budget_slider.setMaximum(300000)
        self.budget_slider.setTickInterval(10000)
        self.budget_slider.setSingleStep(10000)
        self.budget_slider.setValue(self.settings["budget_per_meal"])
        self.budget_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.budget_value_label = QLabel(format_currency(self.settings["budget_per_meal"]))
        
        self.budget_slider.valueChanged.connect(self._on_budget_changed)
        
        budget_slider_layout.addWidget(budget_slider_label)
        budget_slider_layout.addWidget(self.budget_slider)
        budget_slider_layout.addWidget(self.budget_value_label)
        
        # Budget presets
        budget_presets_layout = QHBoxLayout()
        budget_presets_label = QLabel("Hoặc chọn:")
        self.budget_presets = QComboBox()
        
        for budget in BUDGET_OPTIONS:
            self.budget_presets.addItem(format_currency(int(budget)), int(budget))
        
        self.budget_presets.currentIndexChanged.connect(self._on_budget_preset_changed)
        
        budget_presets_layout.addWidget(budget_presets_label)
        budget_presets_layout.addWidget(self.budget_presets)
        budget_presets_layout.addStretch()
        
        budget_layout.addLayout(budget_slider_layout)
        budget_layout.addLayout(budget_presets_layout)
        
        # Prep time settings
        prep_time_group = QGroupBox("Thời gian chuẩn bị")
        prep_time_layout = QVBoxLayout(prep_time_group)
        
        # Prep time slider
        prep_time_slider_layout = QHBoxLayout()
        prep_time_slider_label = QLabel("Thời gian tối đa:")
        self.prep_time_slider = QSlider(Qt.Orientation.Horizontal)
        self.prep_time_slider.setMinimum(15)
        self.prep_time_slider.setMaximum(180)
        self.prep_time_slider.setTickInterval(15)
        self.prep_time_slider.setSingleStep(15)
        self.prep_time_slider.setValue(self.settings["max_prep_time"])
        self.prep_time_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.prep_time_value_label = QLabel(format_time(self.settings["max_prep_time"]))
        
        self.prep_time_slider.valueChanged.connect(self._on_prep_time_changed)
        
        prep_time_slider_layout.addWidget(prep_time_slider_label)
        prep_time_slider_layout.addWidget(self.prep_time_slider)
        prep_time_slider_layout.addWidget(self.prep_time_value_label)
        
        # Prep time presets
        prep_time_presets_layout = QHBoxLayout()
        prep_time_presets_label = QLabel("Hoặc chọn:")
        self.prep_time_presets = QComboBox()
        
        for time in PREP_TIME_OPTIONS:
            self.prep_time_presets.addItem(format_time(int(time)), int(time))
        
        self.prep_time_presets.currentIndexChanged.connect(self._on_prep_time_preset_changed)
        
        prep_time_presets_layout.addWidget(prep_time_presets_label)
        prep_time_presets_layout.addWidget(self.prep_time_presets)
        prep_time_presets_layout.addStretch()
        
        prep_time_layout.addLayout(prep_time_slider_layout)
        prep_time_layout.addLayout(prep_time_presets_layout)
        
        # Days selection
        days_group = QGroupBox("Các ngày trong tuần")
        days_layout = QVBoxLayout(days_group)
        
        # Create checkboxes for days
        self.day_checkboxes = {}
        
        for day in DAYS_OF_WEEK:
            checkbox = QCheckBox(day)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._on_days_changed)
            days_layout.addWidget(checkbox)
            self.day_checkboxes[day] = checkbox
        
        # Meals selection
        meals_group = QGroupBox("Các bữa ăn")
        meals_layout = QVBoxLayout(meals_group)
        
        # Create checkboxes for meals
        self.meal_checkboxes = {}
        
        for meal in MEALS_PER_DAY:
            checkbox = QCheckBox(meal)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._on_meals_changed)
            meals_layout.addWidget(checkbox)
            self.meal_checkboxes[meal] = checkbox
        
        # Day and meal layout
        day_meal_layout = QHBoxLayout()
        day_meal_layout.addWidget(days_group)
        day_meal_layout.addWidget(meals_group)
        
        # Apply button
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Áp dụng thiết lập")
        self.apply_button.clicked.connect(self._apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        
        # Add all components to main layout
        main_layout.addWidget(budget_group)
        main_layout.addWidget(prep_time_group)
        main_layout.addLayout(day_meal_layout)
        main_layout.addLayout(button_layout)
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
    
    def _on_days_changed(self):
        """Handle days selection change."""
        self.settings["days"] = [
            day for day, checkbox in self.day_checkboxes.items()
            if checkbox.isChecked()
        ]
    
    def _on_meals_changed(self):
        """Handle meals selection change."""
        self.settings["meals_per_day"] = [
            meal for meal, checkbox in self.meal_checkboxes.items()
            if checkbox.isChecked()
        ]
    
    def _apply_settings(self):
        """Apply the current settings."""
        self.budget_settings_changed.emit(self.settings.copy()) 