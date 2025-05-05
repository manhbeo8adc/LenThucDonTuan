import logging
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRectF, QSize
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtWidgets import QApplication

# Configure logging
logger = logging.getLogger(__name__)

class ToastNotification(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing ToastNotification")
        try:
            self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(219, 112, 147, 180);  /* PaleVioletRed with transparency */
                    color: white;
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            self.setAlignment(Qt.AlignCenter)
            self.hide()
            
            # Animation for position
            self.pos_animation = QPropertyAnimation(self, b"pos")
            self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.pos_animation.finished.connect(self.hide)
            
            # Animation for opacity
            self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
            self.opacity_animation.setStartValue(1.0)
            self.opacity_animation.setEndValue(0.0)
            self.opacity_animation.setDuration(300)
            
            # Timer for auto-hide
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.hide_animation)
            
            logger.info("ToastNotification initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ToastNotification: {str(e)}")
            raise
    
    def show_message(self, message, duration=1000):
        """Show a toast message for the specified duration in milliseconds."""
        try:
            logger.info(f"Showing toast message: {message}")
            self.setText(message)
            self.adjustSize()
            
            # Get screen geometry
            screen = QApplication.primaryScreen().geometry()
            
            # Calculate center position
            x = screen.center().x() - self.width() // 2
            y = screen.center().y() - self.height() // 2
            
            # Move to center
            self.move(x, y)
            logger.debug(f"Toast positioned at: x={x}, y={y}")
            
            # Reset opacity
            self.setWindowOpacity(1.0)
            
            # Show
            self.show()
            self.raise_()
            
            # Start hide animation immediately
            self.hide_animation()
            logger.info("Toast message shown successfully")
        except Exception as e:
            logger.error(f"Error showing toast message: {str(e)}")
            raise
    
    def hide_animation(self):
        """Animate the toast out of view."""
        try:
            logger.info("Starting hide animation")
            if self.parent():
                start_pos = self.pos()
                # Move down slightly
                end_pos = QPoint(start_pos.x(), start_pos.y() + 30)
                
                # Start both animations
                self.pos_animation.setStartValue(start_pos)
                self.pos_animation.setEndValue(end_pos)
                self.pos_animation.setDuration(800)  # Slower animation
                self.pos_animation.setEasingCurve(QEasingCurve.InOutCubic)
                
                # Configure opacity animation
                self.opacity_animation.setDuration(800)  # Match position animation duration
                self.opacity_animation.setEasingCurve(QEasingCurve.InOutCubic)
                
                self.pos_animation.start()
                self.opacity_animation.start()
                
                logger.debug(f"Animation started from {start_pos} to {end_pos}")
            else:
                self.hide()
                logger.info("Toast hidden (no parent)")
        except Exception as e:
            logger.error(f"Error in hide animation: {str(e)}")
            raise
    
    def paintEvent(self, event):
        """Custom paint event to add rounded corners."""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create rounded rectangle path
            path = QPainterPath()
            # Convert QRect to QRectF
            rect = self.rect()
            rect_f = QRectF(rect.x(), rect.y(), rect.width(), rect.height())
            path.addRoundedRect(rect_f, 10, 10)
            
            # Fill with background color - PaleVioletRed with transparency
            painter.fillPath(path, QColor(219, 112, 147, 180))
            
            # Draw text
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        except Exception as e:
            logger.error(f"Error in paintEvent: {str(e)}")
            raise 