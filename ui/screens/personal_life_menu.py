from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QPainter

class PersonalLifeScreen(QWidget):
    go_back = Signal()
    state_changed = Signal()
    sleep_clicked = Signal()
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        from ui.renderer import SceneComposer
        pixmap = SceneComposer.compose_house(self.state)
        painter.drawPixmap(self.rect(), pixmap)
        
    def update_ui(self):
        self.update()
