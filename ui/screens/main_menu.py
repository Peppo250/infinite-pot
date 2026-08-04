# ui/screens/main_menu.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal
from ui.theme import ThemeManager
from ui.audio import UIAudio

class MainMenuScreen(QWidget):
    start_game = Signal()
    quit_game = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Style Main Menu with retro pixel background
        self.setStyleSheet(f"""
            MainMenuScreen {{
                background-image: url(assets/images/title_bg.jpg);
                background-position: center;
                background-repeat: no-repeat;
            }}
            QLabel {{
                background-color: rgba(252, 248, 242, 0.85);
                border: 2px solid {ThemeManager.DARK_BROWN};
                border-radius: 0px;
                padding: 6px;
            }}
            QPushButton {{
                min-width: 200px;
            }}
        """)
        
        # Add top stretch to push content down
        layout.addStretch()
        
        # Logo / Title
        self.logo_label = QLabel("🍲  INFINITE POT  🍲", self)
        self.logo_label.setStyleSheet(f"""
            font-family: "{ThemeManager.HEADER_FONT}";
            font-size: 32px;
            font-weight: bold;
            color: {ThemeManager.DARK_BROWN};
            margin-bottom: 5px;
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        
        self.subtitle = QLabel("Build a Business to Build a Life", self)
        self.subtitle.setStyleSheet(f"""
            font-size: 26px;
            font-style: italic;
            color: {ThemeManager.DARK_CHARCOAL};
            margin-bottom: 40px;
        """)
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle, alignment=Qt.AlignCenter)
        
        # Menu options
        self.new_game_btn = QPushButton("Start Culinary Journey", self)
        self.new_game_btn.setObjectName("primary-action-btn")
        self.new_game_btn.setMinimumWidth(250)
        self.new_game_btn.clicked.connect(self.on_start_clicked)
        layout.addWidget(self.new_game_btn, alignment=Qt.AlignCenter)
        
        layout.addSpacing(10)
        
        self.credits_btn = QPushButton("View Credits", self)
        self.credits_btn.setMinimumWidth(250)
        self.credits_btn.clicked.connect(self.on_credits_clicked)
        layout.addWidget(self.credits_btn, alignment=Qt.AlignCenter)
        
        layout.addSpacing(10)
        
        self.quit_btn = QPushButton("Exit Game", self)
        self.quit_btn.setObjectName("quit-btn")
        self.quit_btn.setMinimumWidth(250)
        self.quit_btn.clicked.connect(self.on_quit_clicked)
        layout.addWidget(self.quit_btn, alignment=Qt.AlignCenter)
        
        # Add bottom stretch to separate menu block and footer
        layout.addStretch()
        
        # Footer
        self.footer = QLabel("V1 Playable Prototype • Made with PySide6 & Pygame", self)
        self.footer.setStyleSheet(f"font-size: 18px; color: {ThemeManager.DARK_BROWN};")
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer, alignment=Qt.AlignCenter)

        # Credits display state
        self.credits_showing = False

    def on_start_clicked(self):
        UIAudio.play_click()
        self.start_game.emit()

    def on_quit_clicked(self):
        UIAudio.play_click()
        self.quit_game.emit()

    def on_credits_clicked(self):
        UIAudio.play_click()
        from ui.dialogs.custom_dialogs import ConfirmDialog
        credits_text = (
            "Infinite Pot V1 Prototype\n\n"
            "Concept & Gameplay: Original Simulation Design\n"
            "Tech Stack: PySide6 Desktop UI Framework & Pygame Audio Mixer\n\n"
            "This prototype validates the core business-to-life loops, "
            "staff recruitment, relationship progression, and rival restaurant marketing dynamics."
        )
        dlg = ConfirmDialog("Game Credits", credits_text, self)
        # Re-purpose yes/no button texts for simple credits display
        dlg.yes_btn.setText("Close")
        dlg.no_btn.setVisible(False)
        dlg.exec()
