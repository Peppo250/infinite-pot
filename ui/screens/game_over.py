# ui/screens/game_over.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from ui.theme import ThemeManager
from ui.audio import UIAudio

class GameOverScreen(QWidget):
    restart_game = Signal()
    quit_game = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        self.status_title = QLabel("Game Over", self)
        self.status_title.setStyleSheet(f"font-size: 42px; font-weight: bold; color: {ThemeManager.RED_WARNING};")
        self.status_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_title)
        
        self.summary_text = QLabel(self)
        self.summary_text.setWordWrap(True)
        self.summary_text.setAlignment(Qt.AlignCenter)
        self.summary_text.setStyleSheet("font-size: 22px; line-height: 1.5; color: #1F1717; margin-bottom: 20px;")
        layout.addWidget(self.summary_text)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        self.restart_btn = QPushButton("Play Again", self)
        self.restart_btn.setObjectName("primary-action-btn")
        self.restart_btn.setMinimumWidth(180)
        self.restart_btn.clicked.connect(self.on_restart_clicked)
        btn_layout.addWidget(self.restart_btn)
        
        self.exit_btn = QPushButton("Exit Game", self)
        self.exit_btn.setObjectName("quit-btn")
        self.exit_btn.setMinimumWidth(180)
        self.exit_btn.clicked.connect(self.on_exit_clicked)
        btn_layout.addWidget(self.exit_btn)
        
        layout.addLayout(btn_layout)

    def on_restart_clicked(self):
        UIAudio.play_click()
        self.restart_game.emit()

    def on_exit_clicked(self):
        UIAudio.play_click()
        self.quit_game.emit()

    def set_results(self, victory: bool, partner_name: str, final_rep: float, final_cash: float, ending_name: str = "", ending_desc: str = ""):
        if victory:
            UIAudio.play_success()
            self.status_title.setText(ending_name if ending_name else "🍲 VICTORY! 🍲")
            self.status_title.setStyleSheet(f"font-size: 34px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
            
            victory_msg = (
                f"<b>Congratulations!</b> You have completed your journey in <b>Infinite Pot</b>!<br/><br/>"
                f"<b>{ending_name}</b><br/>"
                f"{ending_desc}<br/><br/>"
                f"Through it all, you cooked unlimited food with a single pot, yet food was never the challenge. "
                f"Balancing bills, relationships, employees, and time was.<br/><br/>"
                f"<b>Community Standing:</b> {final_rep:.1f}/100.0<br/>"
                f"<b>Ending Cash Balance:</b> ${final_cash:.2f}"
            )
            self.summary_text.setText(victory_msg)
        else:
            self.status_title.setText("💀 Game Over 💀")
            self.status_title.setStyleSheet(f"font-size: 42px; font-weight: bold; color: {ThemeManager.RED_WARNING};")
            
            loss_msg = (
                "You retired from the culinary business or had to close down.<br/><br/>"
                "Sometimes, managing a magical pot, employees, loans, and relationships on a street "
                "peddler budget is too much to carry.<br/><br/>"
                "Don't give up! Oakhaven is always waiting for a fresh chef to try again."
            )
            self.summary_text.setText(loss_msg)
