from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ui.theme import ThemeManager

class GameplayScreen(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(15)
        
        # LEFT COLUMN: Status & Operations
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
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
        left_layout.addWidget(self.threat_banner)
        
        # Status Card
        self.status_card = QFrame(self)
        self.status_card.setObjectName("card-frame")
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setSpacing(10)
        
        status_title = QLabel("🏰 Diner Status & Operations", self)
        status_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        status_layout.addWidget(status_title)
        
        self.status_lbl = QLabel(self)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet("font-size: 14px; line-height: 1.4;")
        status_layout.addWidget(self.status_lbl)
        
        left_layout.addWidget(self.status_card, stretch=1)
        main_layout.addLayout(left_layout, stretch=3)
        
        # RIGHT COLUMN: Environment & Objectives
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        self.env_img = QLabel(self)
        self.env_img.setStyleSheet(f"border: 4px solid {ThemeManager.DARK_BROWN}; border-radius: 0px;")
        pixmap = QPixmap("assets/images/restaurant_bg.jpg")
        self.env_img.setPixmap(pixmap.scaled(320, 180, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        right_column.addWidget(self.env_img, alignment=Qt.AlignCenter)
        
        self.obj_card = QFrame(self)
        self.obj_card.setObjectName("card-frame")
        obj_layout = QVBoxLayout(self.obj_card)
        obj_layout.setSpacing(10)
        
        obj_title = QLabel("🎯 Current Objectives", self)
        obj_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        obj_layout.addWidget(obj_title)
        
        self.obj_content = QLabel(self)
        self.obj_content.setWordWrap(True)
        self.obj_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.obj_content.setStyleSheet("line-height: 1.4;")
        obj_layout.addWidget(self.obj_content)
        
        right_column.addWidget(self.obj_card, stretch=1)
        main_layout.addLayout(right_column, stretch=2)
        
        self.update_ui()
        
    def update_ui(self, evening_mode=False):
        r = self.state.restaurant
        p = self.state.player
        rom = self.state.romance
        h = self.state.house
        c = self.state.competitor
        
        # Competitor threat visibility
        if c.is_active and not c.counter_marketing_active:
            self.threat_banner.setVisible(True)
        else:
            self.threat_banner.setVisible(False)
            
        # Active employees list
        active_employees = self.state.employees.get_active_employees()
        emp_str = ", ".join([f"{e.name} (Skill: {e.skill:.1f})" for e in active_employees]) if active_employees else "None (Solo operation)"
        
        # Build status string
        status_text = (
            f"Diner Name: <b>{r.name}</b><br/>"
            f"Location: <b>Level {r.level} - {r.current_config.name}</b><br/>"
            f"Menu Price: <b>${r.menu_price:.2f} per meal</b><br/>"
            f"Customer Capacity: <b>{r.customer_capacity} guests max</b><br/>"
            f"Economic Multiplier: <b>{self.state.town.economic_multiplier:.1f}x</b><br/>"
            f"Active Employees: <b>{emp_str}</b><br/>"
        )
        self.status_lbl.setText(f"<html><body>{status_text}</body></html>")
        
        # Objectives content
        obj_text = ""
        if r.level == 0:
            obj_text = f"• Save <b>$300.00</b> (upgrade cost) to buy a Second-Hand Roadside Cart.<br/><br/>• Cook directly on the street to serve hungry passersby."
        elif r.level == 1:
            obj_text = f"• Save <b>$300.00</b> (upgrade cost) to upgrade to your Own Roadside Cart.<br/><br/>• Expand your customer capacity and daily earnings."
        elif r.level == 2:
            obj_text = f"• Save <b>$900.00</b> to upgrade to an Edge-of-Town Shop.<br/><br/>• Earn a proper counter, hire employees, and unlock the local Tavern."
        elif r.level == 3:
            obj_text = f"• Save <b>$2500.00</b> to upgrade to a full Town Restaurant.<br/><br/>• Visit the Tavern in the evening to socialize, date, and recruit employees."
        elif r.level == 4 and not h.purchased:
            obj_text = f"• Save <b>$2500.00</b> to purchase your first cozy cottage.<br/><br/>• Go on dates with <b>{rom.partner_name}</b> at the Tavern to boost romance!"
        elif r.level == 4 and h.purchased and not rom.is_co_owner:
            ring_str = "• Purchase a <b>Diamond Engagement Ring</b> ($2500.00) in Personal Life.<br/><br/>" if not rom.has_ring else ""
            obj_text = f"{ring_str}• Propose marriage & co-ownership to <b>{rom.partner_name}</b> (Requires Romance >= 75)."
        elif c.is_active:
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'days_survived_competitor'):
                p_win = p_win.parent()
            days = p_win.days_survived_competitor if p_win else 0
            obj_text = (
                f"• Defend your life and restaurant from Chef Sebastian's aggressive smear campaigns!<br/><br/>"
                f"• Keep Reputation >= 60.0 and Romance >= 80.0.<br/><br/>"
                f"• Survive for <b>{10 - days} days</b> to secure victory."
            )
        else:
            obj_text = "• You have conquered the town, secured marriage, and established the ultimate restaurant!"
            
        self.obj_content.setText(f"<html><body>{obj_text}</body></html>")
