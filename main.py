"""
Main entry point for the application.
"""
import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key in a .env file or as an environment variable.")
        print("Example:")
        print("OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application name and organization
    app.setApplicationName("Lên Thực Đơn Tuần")
    app.setOrganizationName("LenThucDonTuan")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 