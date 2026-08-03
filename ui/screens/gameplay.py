from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter
from ui.theme import ThemeManager

class GameplayScreen(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.evening_mode = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header banner for competitor threat
        self.threat_banner = QFrame(self)
        self.threat_banner.setObjectName("card-frame")
        self.threat_banner.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.RED_WARNING};
                border: 2px solid {ThemeManager.DARK_CHARCOAL};
                border-radius: 8px;
            }}
            QLabel {{ color: white; font-weight: bold; }}
        """)
        threat_layout = QHBoxLayout(self.threat_banner)
        threat_layout.setContentsMargins(10, 10, 10, 10)
        self.threat_text = QLabel("⚠️ Rival Chef Sebastian is sabotaging your reputation! Counter it via Money Mgmt or PR campaigns.", self)
        self.threat_text.setAlignment(Qt.AlignCenter)
        self.threat_text.setWordWrap(True)
        threat_layout.addWidget(self.threat_text)
        main_layout.addWidget(self.threat_banner)
        
        main_layout.addStretch()
        self.update_ui()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        from ui.renderer import SceneComposer
        pixmap = SceneComposer.compose_restaurant(self.state, self.evening_mode)
        painter.drawPixmap(self.rect(), pixmap)
        
    def update_ui(self, evening_mode=False):
        self.evening_mode = evening_mode
        c = self.state.competitor
        if c.is_active and not c.counter_marketing_active:
            self.threat_banner.setVisible(True)
        else:
            self.threat_banner.setVisible(False)
        self.update()
