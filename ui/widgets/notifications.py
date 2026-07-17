# ui/widgets/notifications.py
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from ui.theme import ThemeManager

class NotificationWidget(QWidget):
    def __init__(self, message: str, alert_type: str = "info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.SubWindow)
        
        # Color mapping based on type
        bg_color = ThemeManager.BLUE_INFO
        if alert_type == "success":
            bg_color = ThemeManager.GREEN_SUCCESS
        elif alert_type == "warning":
            bg_color = ThemeManager.RED_WARNING
        elif alert_type == "money":
            bg_color = ThemeManager.GOLD_MONEY
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(message, self)
        self.label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {ThemeManager.DARK_CHARCOAL};
            border: 2px solid {ThemeManager.DARK_BROWN};
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: bold;
            font-size: 13px;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        # Opacity effect for fading
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        # Timer to fade out
        self.display_timer = QTimer(self)
        self.display_timer.setInterval(2500)  # Show for 2.5 seconds
        self.display_timer.timeout.connect(self.start_fade_out)
        self.display_timer.start()
        
        # Fade animation
        self.fade_anim = None

    def start_fade_out(self):
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_anim.finished.connect(self.deleteLater)
        self.fade_anim.start()

class NotificationManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        
        self.adjust_size_timer = QTimer(self)
        self.adjust_size_timer.setInterval(100)
        self.adjust_size_timer.timeout.connect(self.fit_parent)
        self.adjust_size_timer.start()

    def fit_parent(self):
        if self.parentWidget():
            parent_rect = self.parentWidget().rect()
            width = 300
            height = parent_rect.height() - 80
            # Position at the top right corner
            self.setGeometry(parent_rect.width() - width - 20, 70, width, height)

    def add_notification(self, message: str, alert_type: str = "info"):
        """Spawn a notification toast."""
        toast = NotificationWidget(message, alert_type, self)
        self.layout.addWidget(toast)
        
        # Animate entry (slide or pop)
        # Note: Qt layout will auto-arrange, but we can play a simple scale/opacity transition
        opacity_effect = toast.opacity_effect
        anim = QPropertyAnimation(opacity_effect, b"opacity")
        anim.setDuration(250)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()
        
        # Prevent animation garbage collection
        toast.entry_anim = anim
