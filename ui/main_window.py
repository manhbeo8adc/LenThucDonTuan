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
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QScreen

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
        
        # Apply application style
        self._apply_application_style()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(QSize(1200, 800))  # Increased minimum size
        
        # Try to set icon
        try:
            # Ensure icons directory exists
            icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
            os.makedirs(icons_dir, exist_ok=True)
            
            # Use platform-specific method to set app icon
            if sys.platform == 'win32':
                import ctypes
                app_id = f'lenthucdontuan.app.{APP_VERSION}'  # arbitrary string
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception as e:
            print(f"Warning: Could not set application icon: {e}")
        
        # Create UI components
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Show initialization message
        self.status_bar.showMessage("Ứng dụng đã sẵn sàng!", 3000)
    
    def _apply_application_style(self):
        """Apply custom styles to the application."""
        # Set font for entire application
        app_font = QFont("Segoe UI", 11)  # Segoe UI is modern and readable
        QApplication.setFont(app_font)
        
        # Create a custom palette with feminine colors
        palette = QPalette()
        
        # Set color scheme - soft pink, lavender, and cream tones
        pink_light = QColor(255, 240, 245)  # Lavender Blush
        pink_accent = QColor(219, 112, 147)  # PaleVioletRed
        lavender = QColor(230, 230, 250)  # Lavender
        cream = QColor(255, 253, 208)  # Light cream/beige
        purple_light = QColor(221, 160, 221)  # Plum
        text_color = QColor(70, 70, 70)  # Dark gray for text
        
        # Window background
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # White base
        palette.setColor(QPalette.WindowText, text_color)
        
        # Buttons
        palette.setColor(QPalette.Button, pink_light)
        palette.setColor(QPalette.ButtonText, text_color)
        
        # All widgets
        palette.setColor(QPalette.Base, QColor(255, 255, 255))  # White
        palette.setColor(QPalette.AlternateBase, lavender)
        
        # Highlight
        palette.setColor(QPalette.Highlight, pink_accent)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Apply the palette
        QApplication.setPalette(palette)
        
        # Set stylesheet for additional styling
        stylesheet = """
        QMainWindow {
            background-color: #FFFFFF;
        }
        
        QTabWidget::pane {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            background-color: #FFFFFF;
        }
        
        QTabBar::tab {
            background-color: #F0F0F0;
            border: 1px solid #CCCCCC;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 16px;
            margin-right: 2px;
            color: #666666;
            font-weight: 500;
        }
        
        QTabBar::tab:selected {
            background-color: #DB7093;
            color: white;
            border-color: #DB7093;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #FFE4E1;
        }
        
        QPushButton {
            background-color: #DB7093;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #C25B7A;
        }
        
        QPushButton:pressed {
            background-color: #A94E69;
        }
        
        QPushButton:disabled {
            background-color: #E6E6E6;
            color: #B3B3B3;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            padding: 8px;
            background-color: #FFFFFF;
            min-height: 20px;
            font-size: 11pt;
            color: black;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 1px solid #DB7093;
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
        
        QLabel {
            color: #444444;
            font-size: 11pt;
        }
        
        QGroupBox {
            border: 1px solid #FFC0CB;
            border-radius: 6px;
            margin-top: 12px;
            font-weight: bold;
            background-color: #FFF5F5;
            padding: 8px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 8px;
            color: #DB7093;
            background-color: #FFFFFF;
            font-size: 12pt;
        }
        
        QListWidget {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            background-color: #FFFFFF;
            alternate-background-color: #FFF5F5;
            padding: 4px;
            font-size: 11pt;
        }
        
        QListWidget::item {
            border-bottom: 1px solid #F0F0F0;
            padding: 8px;
            margin: 2px 0;
            border-radius: 4px;
        }
        
        QListWidget::item:selected {
            background-color: #DB7093;
            color: white;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #FFE4E1;
        }
        
        QSplitter::handle {
            background-color: #F0F0F0;
        }
        
        QSplitter::handle:hover {
            background-color: #DB7093;
        }
        
        QMenuBar {
            background-color: #FFF0F5;
            border-bottom: 1px solid #EEEEEE;
        }
        
        QMenuBar::item {
            padding: 6px 12px;
            background: transparent;
        }
        
        QMenuBar::item:selected {
            background-color: #DB7093;
            color: white;
        }
        
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #EEEEEE;
        }
        
        QMenu::item {
            padding: 6px 24px 6px 20px;
        }
        
        QMenu::item:selected {
            background-color: #DB7093;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #FFF0F5;
            padding: 6px;
            border: 1px solid #EEEEEE;
            font-weight: bold;
        }
        
        QProgressBar {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            text-align: center;
            background-color: #FFFFFF;
        }
        
        QProgressBar::chunk {
            background-color: #DB7093;
            width: 20px;
        }
        
        QCheckBox {
            spacing: 8px;
            font-size: 11pt;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QRadioButton {
            spacing: 8px;
            font-size: 11pt;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #FAFAFA;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #DB7093;
            min-height: 30px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #C25B7A;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #FAFAFA;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #DB7093;
            min-width: 30px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #C25B7A;
        }
        
        QSpinBox, QDoubleSpinBox {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            padding: 4px;
            background-color: #FFFFFF;
            min-height: 20px;
            font-size: 11pt;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #DB7093;
        }
        
        QDateEdit, QTimeEdit {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            padding: 4px;
            background-color: #FFFFFF;
            font-size: 11pt;
        }
        
        QDateEdit:focus, QTimeEdit:focus {
            border: 1px solid #DB7093;
        }
        
        QStatusBar {
            background-color: #FFF0F5;
            color: #555555;
        }
        
        QStatusBar QLabel {
            font-size: 10pt;
        }
        
        QToolTip {
            background-color: #FFF0F5;
            color: #444444;
            border: 1px solid #DB7093;
            border-radius: 4px;
            padding: 4px;
        }
        
        /* Styling for RecipeDialog content */
        QTextEdit.recipe-steps {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333333;
            background-color: #FFFFFF;
            padding: 12px;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
        }
        
        QLabel.step-label {
            font-weight: bold;
            font-size: 11pt;
            color: #DB7093;
            margin-bottom: 4px;
        }
        
        QLabel.ingredient-label {
            font-weight: bold;
            font-size: 11pt;
            color: #2E8B57;
            margin-bottom: 4px;
        }
        """
        
        self.setStyleSheet(stylesheet)
    
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
        """Create and set the central widget."""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Create tab widget for all panels
        self.tab_widget = QTabWidget()
        
        # Add toast notification container (a label that will appear temporarily)
        self.toast_container = QLabel(self)
        self.toast_container.setAlignment(Qt.AlignCenter)
        self.toast_container.setStyleSheet("""
            background-color: rgba(219, 112, 147, 0.9);
            color: white;
            border-radius: 15px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12pt;
        """)
        self.toast_container.hide()
        self.toast_timer = QTimer(self)
        self.toast_timer.timeout.connect(self._hide_toast)
        
        # Add a welcome message at the top
        welcome_label = QLabel(f"Chào mừng đến với <b>{APP_NAME}</b>! " 
                               f"Hãy tạo thực đơn tuần phù hợp với sở thích của bạn.")
        welcome_label.setStyleSheet("font-size: 14pt; color: #DB7093; margin-bottom: 10px;")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # Create panels
        self.preferences_panel = PreferencesPanel(self.db_manager)
        self.cuisine_panel = CuisinePanel()
        self.budget_panel = BudgetPanel()
        self.menu_panel = MenuPanel(self.api, self.db_manager)
        
        # Connect panels to each other
        self.preferences_panel.user_selected.connect(self.menu_panel.set_user)
        self.cuisine_panel.cuisine_selected.connect(self.menu_panel.set_cuisine)
        self.budget_panel.budget_settings_changed.connect(self.menu_panel.set_budget_settings)
        
        # Create icons based on unicode characters
        preferences_icon = self.style().standardIcon(self.style().SP_DialogYesButton)
        cuisine_icon = self.style().standardIcon(self.style().SP_FileDialogInfoView)
        budget_icon = self.style().standardIcon(self.style().SP_DialogApplyButton)
        menu_icon = self.style().standardIcon(self.style().SP_FileDialogDetailedView)
        
        # Add panels to tabs with icons
        self.tab_widget.addTab(self.preferences_panel, preferences_icon, "Sở thích")
        self.tab_widget.addTab(self.cuisine_panel, cuisine_icon, "Phong cách ẩm thực")
        self.tab_widget.addTab(self.budget_panel, budget_icon, "Ngân sách & Thời gian")
        self.tab_widget.addTab(self.menu_panel, menu_icon, "Thực đơn")
        
        # Add welcome label and tab widget to main layout
        layout.addWidget(welcome_label)
        layout.addWidget(self.tab_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def _create_status_bar(self):
        """Create and set the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def show_toast(self, message, duration=2000):
        """Show a toast notification that fades out after a few seconds.
        Args:
            message: The message to display
            duration: How long to display the message in milliseconds
        """
        # Position the toast in the center top of the window
        screen_geometry = self.geometry()
        self.toast_container.setText(message)
        self.toast_container.adjustSize()
        
        # Calculate position - centered horizontally, 15% down from the top
        toast_width = self.toast_container.width()
        toast_height = self.toast_container.height()
        x_position = int((screen_geometry.width() - toast_width) / 2)
        y_position = int(screen_geometry.height() * 0.15)
        
        self.toast_container.setGeometry(x_position, y_position, toast_width, toast_height)
        self.toast_container.show()
        
        # Stop any existing timer
        if self.toast_timer.isActive():
            self.toast_timer.stop()
        
        # Start timer to hide the toast
        self.toast_timer.start(duration)
    
    def _hide_toast(self):
        """Hide the toast notification."""
        self.toast_timer.stop()
        self.toast_container.hide()
    
    def _update_progress(self, message: str):
        """Update progress bar and status message."""
        if message.startswith("Đang tạo"):
            self.progress_bar.setMaximum(0)  # Indeterminate progress
            self.progress_bar.show()
            self.status_bar.showMessage(f"🔄 {message}", 3000)
        elif message.startswith("Đã hoàn thành"):
            self.progress_bar.hide()
            self.status_bar.showMessage(f"✅ {message}", 3000)
        else:
            self.status_bar.showMessage(f"ℹ️ {message}", 3000)
    
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
        """Show about dialog."""
        about_text = f"""
        <div style="text-align: center;">
            <h2 style="color: #DB7093;">{APP_NAME}</h2>
            <p style="font-size: 10pt;">Phiên bản {APP_VERSION}</p>
            <p>Ứng dụng giúp lên thực đơn tuần dễ dàng, tiết kiệm thời gian<br/>
            và tối ưu nguyên liệu dựa trên sở thích cá nhân.</p>
            
            <p style="margin-top: 20px; font-weight: bold; color: #DB7093;">Tính năng chính:</p>
            <ul style="text-align: left; margin-left: 30px;">
                <li>Tạo thực đơn tuần theo sở thích cá nhân</li>
                <li>Tối ưu hóa nguyên liệu giữa các bữa</li>
                <li>Tính toán ngân sách và thời gian nấu nướng</li>
                <li>Cung cấp công thức chi tiết cho từng món ăn</li>
                <li>Lưu và quản lý thực đơn hàng tuần</li>
            </ul>
            
            <p style="margin-top: 20px; font-size: 9pt; color: #888888;">
            Được phát triển nhằm giúp người nội trợ tiết kiệm thời gian<br/>
            và tạo ra những bữa ăn đa dạng cho gia đình.<br/>
            Sử dụng trí tuệ nhân tạo của OpenAI để gợi ý món ăn phù hợp.
            </p>
        </div>
        """
        
        QMessageBox.about(self, f"Giới thiệu {APP_NAME}", about_text)
    
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