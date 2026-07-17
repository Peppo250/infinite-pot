# ui/theme.py
import os
from PySide6.QtGui import QFontDatabase

class ThemeManager:
    # Cozy retro pixel-art color palette (Stardew Valley / Traveller's Rest style)
    CREAM = "#FCF8F2"
    WARM_BEIGE = "#EADBC8"
    MEDIUM_BEIGE = "#DAC0A3"
    DARK_BROWN = "#5B3923"
    DARK_CHARCOAL = "#221A1A"
    
    # Accent colors
    GREEN_SUCCESS = "#7BC676"
    GOLD_MONEY = "#E5BA73"
    RED_WARNING = "#C84B31"
    BLUE_INFO = "#6B85C1"
    
    FONT_FAMILY = "VT323"          # Primary retro dialog font
    HEADER_FONT = "Press Start 2P" # Classic blocky header font
    
    @classmethod
    def initialize(cls):
        """Loads the pixel fonts dynamically from the assets folder."""
        font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")
        
        # Load VT323
        vt323_path = os.path.join(font_dir, "VT323-Regular.ttf")
        if os.path.exists(vt323_path):
            fid = QFontDatabase.addApplicationFont(vt323_path)
            if fid != -1:
                families = QFontDatabase.applicationFontFamilies(fid)
                if families:
                    cls.FONT_FAMILY = families[0]
                    
        # Load Press Start 2P
        ps2p_path = os.path.join(font_dir, "PressStart2P-Regular.ttf")
        if os.path.exists(ps2p_path):
            fid = QFontDatabase.addApplicationFont(ps2p_path)
            if fid != -1:
                families = QFontDatabase.applicationFontFamilies(fid)
                if families:
                    cls.HEADER_FONT = families[0]
    
    @classmethod
    def get_style_sheet(cls) -> str:
        """Returns the retro pixel-art style sheet (QSS) for the application."""
        return f"""
            QWidget {{
                background-color: {cls.CREAM};
                color: {cls.DARK_CHARCOAL};
                font-family: "{cls.FONT_FAMILY}", "Courier New", monospace;
                font-size: 20px;
            }}
            
            QMainWindow {{
                background-color: {cls.CREAM};
            }}
            
            QLabel {{
                background-color: transparent;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QLabel#title-label {{
                font-family: "{cls.HEADER_FONT}", Arial, sans-serif;
                font-size: 20px;
                font-weight: bold;
                color: {cls.DARK_BROWN};
                margin-bottom: 5px;
            }}
            
            QLabel#subtitle-label {{
                font-size: 16px;
                color: {cls.DARK_BROWN};
                font-style: italic;
            }}
            
            QLabel#hud-label {{
                font-weight: bold;
                font-size: 18px;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QLabel#hud-value {{
                font-size: 20px;
                font-weight: bold;
                color: {cls.DARK_BROWN};
            }}
            
            QPushButton {{
                background-color: {cls.WARM_BEIGE};
                border: 3px solid {cls.DARK_BROWN};
                border-radius: 0px;
                padding: 6px 12px;
                font-weight: bold;
                color: {cls.DARK_CHARCOAL};
                min-height: 24px;
            }}
            
            QPushButton:hover {{
                background-color: {cls.MEDIUM_BEIGE};
                border-color: {cls.DARK_CHARCOAL};
            }}
            
            QPushButton:pressed {{
                background-color: {cls.DARK_BROWN};
                color: {cls.CREAM};
                border-color: {cls.DARK_CHARCOAL};
            }}
            
            QPushButton:disabled {{
                background-color: #D3D3D3;
                border-color: #A0A0A0;
                color: #7E7E7E;
            }}
            
            QPushButton#primary-action-btn {{
                background-color: {cls.GOLD_MONEY};
                border: 3px solid {cls.DARK_BROWN};
            }}
            
            QPushButton#primary-action-btn:hover {{
                background-color: {cls.WARM_BEIGE};
            }}
            
            QPushButton#quit-btn {{
                background-color: {cls.RED_WARNING};
                color: white;
                border: 3px solid {cls.DARK_CHARCOAL};
            }}
            
            QPushButton#quit-btn:hover {{
                background-color: #A03D2E;
            }}
            
            QProgressBar {{
                border: 3px solid {cls.DARK_BROWN};
                border-radius: 0px;
                text-align: center;
                font-weight: bold;
                background-color: white;
                height: 24px;
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.GOLD_MONEY};
                border-radius: 0px;
            }}
            
            QFrame#card-frame {{
                background-color: white;
                border: 4px solid {cls.DARK_BROWN};
                border-radius: 0px;
                padding: 8px;
            }}
            
            QFrame#hud-bar {{
                background-color: {cls.WARM_BEIGE};
                border-bottom: 4px solid {cls.DARK_BROWN};
                padding: 4px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: 3px solid {cls.DARK_BROWN};
                background-color: {cls.CREAM};
                width: 14px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.MEDIUM_BEIGE};
                min-height: 20px;
                border-radius: 0px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.DARK_BROWN};
            }}
            
            QListWidget {{
                background-color: white;
                border: 3px solid {cls.DARK_BROWN};
                border-radius: 0px;
                padding: 5px;
            }}
            
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                background-color: white;
                border: 3px solid {cls.DARK_BROWN};
                border-radius: 0px;
                padding: 4px;
                font-size: 18px;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                background-color: #FAF8F5;
            }}
            
            QTabWidget::pane {{
                border: 4px solid {cls.DARK_BROWN};
                border-radius: 0px;
                background-color: white;
            }}
            
            QTabBar::tab {{
                background: {cls.WARM_BEIGE};
                border: 3px solid {cls.DARK_BROWN};
                border-bottom-color: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                padding: 6px 12px;
                font-weight: bold;
                color: {cls.DARK_CHARCOAL};
                margin-right: 4px;
            }}
            
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: white;
                border-bottom-color: white;
            }}
            
            QSlider::groove:horizontal {{
                border: 2px solid {cls.DARK_BROWN};
                height: 10px;
                background: white;
            }}

            QSlider::handle:horizontal {{
                background: {cls.GOLD_MONEY};
                border: 2px solid {cls.DARK_BROWN};
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
            }}
        """
