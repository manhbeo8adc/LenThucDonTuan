"""
Cuisine selection panel for the application.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QRadioButton,
    QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal

from config import CUISINE_TYPES


class CuisinePanel(QWidget):
    """Panel for selecting cuisine type."""
    
    # Signal emitted when a cuisine is selected
    cuisine_selected = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the panel."""
        super().__init__()
        
        self.selected_cuisine = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Chọn phong cách ẩm thực")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Description
        description_label = QLabel(
            "Chọn phong cách ẩm thực sẽ ảnh hưởng đến các món ăn được gợi ý. "
            "Mỗi phong cách ẩm thực có những đặc trưng riêng về nguyên liệu và cách chế biến."
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)
        
        # Cuisine selection
        cuisine_group = QGroupBox("Phong cách ẩm thực")
        cuisine_layout = QVBoxLayout(cuisine_group)
        
        self.cuisine_button_group = QButtonGroup(self)
        
        # Style for radio buttons
        radio_button_style = """
            QRadioButton {
                font-size: 12pt;
                padding: 6px;
                spacing: 8px; /* Space between radio button and text */
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton:hover {
                background-color: #FFF0F5;
                border-radius: 4px;
            }
        """
        
        # Add cuisine options
        for cuisine in CUISINE_TYPES:
            radio_button = QRadioButton(cuisine)
            radio_button.setProperty("cuisine", cuisine)
            radio_button.setStyleSheet(radio_button_style)
            self.cuisine_button_group.addButton(radio_button)
            cuisine_layout.addWidget(radio_button)
        
        # Connect button group
        self.cuisine_button_group.buttonClicked.connect(self._on_cuisine_selected)
        
        main_layout.addWidget(cuisine_group)
        
        # Cuisine details
        self.details_group = QGroupBox("Chi tiết phong cách ẩm thực")
        details_layout = QVBoxLayout(self.details_group)
        
        self.cuisine_name_label = QLabel()
        self.cuisine_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.cuisine_description_label = QLabel()
        self.cuisine_description_label.setWordWrap(True)
        
        self.cuisine_ingredients_label = QLabel()
        self.cuisine_ingredients_label.setWordWrap(True)
        
        details_layout.addWidget(self.cuisine_name_label)
        details_layout.addWidget(self.cuisine_description_label)
        details_layout.addWidget(self.cuisine_ingredients_label)
        
        main_layout.addWidget(self.details_group)
        self.details_group.setVisible(False)
        
        # Button
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("Sử dụng phong cách ẩm thực này")
        self.select_button.clicked.connect(self._select_cuisine)
        self.select_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.select_button)
        
        main_layout.addLayout(button_layout)
        
        # Add stretch at the end
        main_layout.addStretch()
    
    def _on_cuisine_selected(self, button):
        """Handle cuisine selection."""
        self.selected_cuisine = button.property("cuisine")
        
        # Update details
        self._update_cuisine_details()
        
        # Enable select button
        self.select_button.setEnabled(True)
    
    def _update_cuisine_details(self):
        """Update cuisine details."""
        if not self.selected_cuisine:
            self.details_group.setVisible(False)
            return
        
        self.cuisine_name_label.setText(self.selected_cuisine)
        
        # Display cuisine details based on selection
        details = self._get_cuisine_details(self.selected_cuisine)
        
        self.cuisine_description_label.setText(f"<b>Đặc điểm:</b> {details['description']}")
        self.cuisine_ingredients_label.setText(f"<b>Nguyên liệu phổ biến:</b> {', '.join(details['ingredients'])}")
        
        self.details_group.setVisible(True)
    
    def _select_cuisine(self):
        """Emit signal to indicate the cuisine is selected."""
        if self.selected_cuisine:
            self.cuisine_selected.emit(self.selected_cuisine)
            
            # Get the main window to show toast notification
            main_window = self.window()
            if hasattr(main_window, 'show_toast'):
                main_window.show_toast(f"Đã chọn phong cách: {self.selected_cuisine}")
    
    def _get_cuisine_details(self, cuisine):
        """Get details for a specific cuisine."""
        # This could be loaded from a database or config file
        # For now, using hardcoded values
        cuisine_details = {
            "Ẩm thực miền Nam Việt Nam": {
                "description": "Ẩm thực miền Nam Việt Nam thường có vị ngọt, cay và chua, sử dụng nhiều nước cốt dừa và đường.",
                "ingredients": ["Nước cốt dừa", "Đường", "Rau thơm", "Cá", "Tôm", "Thịt heo", "Bún", "Rau muống"]
            },
            "Ẩm thực miền Bắc Việt Nam": {
                "description": "Ẩm thực miền Bắc Việt Nam thường nhẹ nhàng, cân bằng, ít cay, ít ngọt hơn so với miền Nam.",
                "ingredients": ["Hành", "Tỏi", "Nước mắm", "Thịt bò", "Thịt gà", "Rau thơm", "Bún", "Phở"]
            },
            "Ẩm thực miền Trung Việt Nam": {
                "description": "Ẩm thực miền Trung Việt Nam nổi tiếng với vị cay nồng và các món ăn tinh tế, nhiều màu sắc.",
                "ingredients": ["Ớt", "Nước mắm", "Tôm", "Thịt heo", "Bún", "Bánh", "Lá chuối"]
            },
            "Ẩm thực Pháp": {
                "description": "Ẩm thực Pháp nổi tiếng với sự tinh tế, kỹ thuật chế biến phức tạp và các loại nước sốt đa dạng.",
                "ingredients": ["Bơ", "Rượu vang", "Kem", "Phô mai", "Thịt bò", "Nấm", "Rau củ theo mùa"]
            },
            "Ẩm thực Ý": {
                "description": "Ẩm thực Ý đơn giản, tập trung vào nguyên liệu tươi ngon và cách chế biến đơn giản.",
                "ingredients": ["Mì Ý", "Cà chua", "Dầu ô liu", "Phô mai", "Thịt bò", "Rau húng quế", "Tỏi"]
            },
            "Ẩm thực Trung Hoa": {
                "description": "Ẩm thực Trung Hoa đa dạng theo vùng miền, nổi tiếng với kỹ thuật chiên, xào nhanh và đa dạng gia vị.",
                "ingredients": ["Nước tương", "Dầu mè", "Gừng", "Tỏi", "Hành lá", "Thịt heo", "Thịt gà", "Đậu phụ"]
            },
            "Ẩm thực Nhật Bản": {
                "description": "Ẩm thực Nhật Bản tinh tế, tối giản, tôn trọng hương vị tự nhiên của nguyên liệu.",
                "ingredients": ["Gạo", "Cá sống", "Rong biển", "Nước tương", "Wasabi", "Mirin", "Sake"]
            },
            "Ẩm thực Hàn Quốc": {
                "description": "Ẩm thực Hàn Quốc nổi tiếng với các món ăn cay, lên men và nhiều rau củ.",
                "ingredients": ["Kim chi", "Gochujang (tương ớt)", "Gạo", "Thịt bò", "Thịt heo", "Rau củ", "Đậu nành"]
            },
            "Ẩm thực Thái Lan": {
                "description": "Ẩm thực Thái Lan cân bằng giữa các vị cay, chua, ngọt, mặn và thường có mùi thơm từ các loại rau thơm.",
                "ingredients": ["Sả", "Gừng", "Nước cốt dừa", "Ớt", "Nước mắm", "Chanh", "Rau thơm"]
            },
            "Ẩm thực Ấn Độ": {
                "description": "Ẩm thực Ấn Độ phong phú về gia vị, đa dạng theo vùng miền và có nhiều món chay.",
                "ingredients": ["Cà ri", "Garam masala", "Đậu", "Sữa chua", "Bánh mì", "Gạo", "Rau củ"]
            }
        }
        
        return cuisine_details.get(cuisine, {
            "description": "Không có thông tin chi tiết.",
            "ingredients": []
        }) 