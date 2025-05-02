"""
Main entry point for the application.
"""
import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox, QLineEdit

from ui.main_window import MainWindow
from utils.api_key_manager import get_api_key, save_api_key


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application name and organization
    app.setApplicationName("Lên Thực Đơn Tuần")
    app.setOrganizationName("LenThucDonTuan")
    
    # Check for API key in environment or encrypted file
    api_key = get_api_key()
    if not api_key:
        QMessageBox.information(
            None,
            "OpenAI API Key Required",
            "Ứng dụng cần OpenAI API Key để hoạt động.\n\n"
            "Bạn có thể lấy API key từ trang:\n"
            "https://platform.openai.com/api-keys"
        )
        
        api_key, ok = QInputDialog.getText(
            None, 
            "Nhập OpenAI API Key",
            "Vui lòng nhập OpenAI API Key của bạn:",
            QLineEdit.Password
        )
        
        if not ok or not api_key:
            QMessageBox.critical(
                None,
                "Không thể tiếp tục",
                "Ứng dụng cần OpenAI API Key để hoạt động.\nỨng dụng sẽ đóng."
            )
            sys.exit(1)
        
        # Save API key to encrypted file
        save_api_key(api_key)
        
        # Set the API key in environment for current session
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 