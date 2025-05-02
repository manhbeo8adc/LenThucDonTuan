"""
Main window UI for the application.
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QFileDialog, QAction, QProgressBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from config import APP_NAME, APP_VERSION
from database.db_manager import DatabaseManager
from api.openai_api import OpenAIWrapper
from utils.helpers import save_json, load_json, export_menu_to_text, ensure_directory_exists

# Import UI panels
from .preferences_panel import PreferencesPanel
from .cuisine_panel import CuisinePanel
from .budget_panel import BudgetPanel
from .menu_panel import MenuPanel


class MainWindow(QMainWindow):
    """Main window of the application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize database and API
        self.db_manager = DatabaseManager()
        self.api = OpenAIWrapper()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(QSize(1200, 800))  # Increased minimum size
        
        # Create UI components
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Show initialization message
        self.status_bar.showMessage("Ứng dụng đã sẵn sàng!", 3000)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New menu
        new_action = QAction("Mới", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_menu)
        file_menu.addAction(new_action)
        
        # Open menu
        open_action = QAction("Mở", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_menu)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save menu
        save_action = QAction("Lưu", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_menu)
        file_menu.addAction(save_action)
        
        # Save as menu
        save_as_action = QAction("Lưu như", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_as_menu)
        file_menu.addAction(save_as_action)
        
        # Export menu
        export_action = QAction("Xuất", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_menu)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Trợ giúp")
        
        # About action
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_central_widget(self):
        """Create the central widget with tabs."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add more padding
        main_layout.setSpacing(10)  # Increase spacing
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create panels
        self.preferences_panel = PreferencesPanel(self.db_manager)
        self.cuisine_panel = CuisinePanel()
        self.budget_panel = BudgetPanel()
        self.menu_panel = MenuPanel(self.api, self.db_manager)
        
        # Connect panels to each other
        self.preferences_panel.user_selected.connect(self.menu_panel.set_user)
        self.cuisine_panel.cuisine_selected.connect(self.menu_panel.set_cuisine)
        self.budget_panel.budget_settings_changed.connect(self.menu_panel.set_budget_settings)
        
        # Add panels to tabs
        self.tab_widget.addTab(self.preferences_panel, "Sở thích")
        self.tab_widget.addTab(self.cuisine_panel, "Phong cách ẩm thực")
        self.tab_widget.addTab(self.budget_panel, "Ngân sách & Thời gian")
        self.tab_widget.addTab(self.menu_panel, "Thực đơn")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()  # Hide by default
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Add status label
        self.status_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_label)
        
        self.setStatusBar(self.status_bar)
        
        # Connect API progress signal
        self.api.progress_signal.connect(self._update_progress)
    
    def _update_progress(self, message: str):
        """Update progress bar and status message."""
        if message.startswith("Đang tạo"):
            self.progress_bar.setMaximum(0)  # Indeterminate progress
            self.progress_bar.show()
            self.status_label.setText(message)
        elif message.startswith("Đã hoàn thành"):
            self.progress_bar.hide()
            self.status_label.setText(message)
            self.status_bar.showMessage(message, 3000)  # Show in status bar for 3 seconds
    
    def _new_menu(self):
        """Create a new menu."""
        confirmation = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn tạo thực đơn mới? Thực đơn hiện tại sẽ bị mất nếu chưa được lưu.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            self.menu_panel.clear_menu()
            self.tab_widget.setCurrentWidget(self.preferences_panel)
            self.status_bar.showMessage("Đã tạo thực đơn mới", 3000)
    
    def _open_menu(self):
        """Open a saved menu."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Mở thực đơn",
            "",
            "JSON Files (*.json)"
        )
        
        if file_name:
            data = load_json(file_name)
            if data:
                if self.menu_panel.load_menu(data):
                    self.tab_widget.setCurrentWidget(self.menu_panel)
                    self.status_bar.showMessage(f"Đã mở thực đơn từ {file_name}", 3000)
                else:
                    QMessageBox.warning(
                        self,
                        "Lỗi",
                        "Không thể tải thực đơn từ tệp đã chọn"
                    )
    
    def _save_menu(self):
        """Save the current menu."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu thực đơn",
            "",
            "JSON Files (*.json)"
        )
        
        if file_name:
            if not file_name.endswith('.json'):
                file_name += '.json'
            
            data = self.menu_panel.get_menu_data()
            if save_json(data, file_name):
                self.status_bar.showMessage(f"Đã lưu thực đơn vào {file_name}", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "Lỗi",
                    "Không thể lưu thực đơn"
                )
    
    def _save_as_menu(self):
        """Save the current menu with a new name."""
        # This is effectively the same as _save_menu for now
        self._save_menu()
    
    def _export_menu(self):
        """Export the current menu to a text file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất thực đơn",
            "",
            "Text Files (*.txt)"
        )
        
        if file_name:
            if not file_name.endswith('.txt'):
                file_name += '.txt'
            
            data = self.menu_panel.get_menu_data()
            if data and export_menu_to_text(data['menu'], file_name):
                self.status_bar.showMessage(f"Đã xuất thực đơn vào {file_name}", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "Lỗi",
                    "Không thể xuất thực đơn"
                )
    
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "Giới thiệu",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Ứng dụng giúp lập kế hoạch thực đơn tuần dựa trên sở thích cá nhân, "
            "ngân sách, và thời gian chuẩn bị, với tính năng tối ưu nguyên liệu giữa các bữa ăn."
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        confirmation = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn thoát khỏi ứng dụng? Mọi thay đổi chưa lưu sẽ bị mất.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore() 