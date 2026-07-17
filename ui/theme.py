# ui/theme.py
from PySide6.QtGui import QColor

class ThemeManager:
    # Color palette
    CREAM = "#FCF8F2"
    WARM_BEIGE = "#EADBC8"
    MEDIUM_BEIGE = "#DAC0A3"
    DARK_BROWN = "#7F5539"
    DARK_CHARCOAL = "#1F1717"
    
    # Accent colors
    GREEN_SUCCESS = "#8ADAB2"
    GOLD_MONEY = "#E1AA74"
    RED_WARNING = "#E25E3E"
    BLUE_INFO = "#82A0D8"
    
    FONT_FAMILY = "Segoe UI"
    
    @classmethod
    def get_style_sheet(cls) -> str:
        """Returns the centralized stylesheet for styling widgets."""
        return f"""
            QWidget {{
                background-color: {cls.CREAM};
                color: {cls.DARK_CHARCOAL};
                font-family: "{cls.FONT_FAMILY}", "Nunito", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
            }}
            
            QMainWindow {{
                background-color: {cls.CREAM};
            }}
            
            QLabel {{
                background-color: transparent;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QLabel#title-label {{
                font-size: 28px;
                font-weight: bold;
                color: {cls.DARK_BROWN};
                margin-bottom: 5px;
            }}
            
            QLabel#subtitle-label {{
                font-size: 15px;
                color: {cls.DARK_BROWN};
                font-style: italic;
            }}
            
            QLabel#hud-label {{
                font-weight: bold;
                font-size: 14px;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QLabel#hud-value {{
                font-size: 16px;
                font-weight: bold;
                color: {cls.DARK_BROWN};
            }}
            
            QPushButton {{
                background-color: {cls.WARM_BEIGE};
                border: 2px solid {cls.MEDIUM_BEIGE};
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
                color: {cls.DARK_CHARCOAL};
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {cls.MEDIUM_BEIGE};
                border-color: {cls.DARK_BROWN};
            }}
            
            QPushButton:pressed {{
                background-color: {cls.DARK_BROWN};
                color: {cls.CREAM};
                border-color: {cls.DARK_CHARCOAL};
            }}
            
            QPushButton:disabled {{
                background-color: #E6E6E6;
                border-color: #D3D3D3;
                color: #A0A0A0;
            }}
            
            QPushButton#primary-action-btn {{
                background-color: {cls.GOLD_MONEY};
                border: 2px solid {cls.DARK_BROWN};
            }}
            
            QPushButton#primary-action-btn:hover {{
                background-color: {cls.WARM_BEIGE};
            }}
            
            QPushButton#quit-btn {{
                background-color: {cls.RED_WARNING};
                color: white;
                border: 2px solid {cls.DARK_CHARCOAL};
            }}
            
            QPushButton#quit-btn:hover {{
                background-color: #C24D3D;
            }}
            
            QProgressBar {{
                border: 2px solid {cls.MEDIUM_BEIGE};
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                background-color: white;
                height: 22px;
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.GOLD_MONEY};
                border-radius: 4px;
            }}
            
            QFrame#card-frame {{
                background-color: white;
                border: 2px solid {cls.WARM_BEIGE};
                border-radius: 12px;
                padding: 15px;
            }}
            
            QFrame#hud-bar {{
                background-color: {cls.WARM_BEIGE};
                border-bottom: 2px solid {cls.MEDIUM_BEIGE};
                padding: 5px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background-color: {cls.CREAM};
                width: 10px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.MEDIUM_BEIGE};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.DARK_BROWN};
            }}
            
            QListWidget {{
                background-color: white;
                border: 2px solid {cls.WARM_BEIGE};
                border-radius: 8px;
                padding: 5px;
            }}
            
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                background-color: white;
                border: 2px solid {cls.WARM_BEIGE};
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {cls.DARK_BROWN};
            }}
            
            QTabWidget::pane {{
                border: 2px solid {cls.WARM_BEIGE};
                border-radius: 8px;
                background-color: white;
            }}
            
            QTabBar::tab {{
                background: {cls.WARM_BEIGE};
                border: 2px solid {cls.MEDIUM_BEIGE};
                border-bottom-color: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                color: {cls.DARK_CHARCOAL};
            }}
            
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: white;
                border-color: {cls.WARM_BEIGE};
                border-bottom-color: white;
            }}
        """
