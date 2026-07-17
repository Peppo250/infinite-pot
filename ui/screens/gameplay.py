from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame, QGroupBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from ui.theme import ThemeManager
from ui.audio import UIAudio

class GameplayScreen(QWidget):
    manage_business = Signal()
    personal_life = Signal()
    restaurant_opened = Signal(int)  # Emits selected work hours
    go_to_tavern = Signal()
    sleep_clicked = Signal()
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # LEFT COLUMN: Business Operations
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
        self.threat_text = QLabel("⚠️ Rival Chef Sebastian is sabotaging your reputation! Counter it in Business Management.", self)
        self.threat_text.setAlignment(Qt.AlignCenter)
        self.threat_text.setWordWrap(True)
        threat_layout.addWidget(self.threat_text)
        left_layout.addWidget(self.threat_banner)
        
        # Operation Control Card
        self.control_card = QFrame(self)
        self.control_card.setObjectName("card-frame")
        control_layout = QVBoxLayout(self.control_card)
        control_layout.setSpacing(10)
        
        control_title = QLabel("Restaurant Operations", self)
        control_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        control_layout.addWidget(control_title)
        
        # Energy tracker readout
        self.energy_readout = QLabel(self)
        self.energy_readout.setStyleSheet("font-size: 14px; font-weight: bold;")
        control_layout.addWidget(self.energy_readout)
        
        # 1. MORNING PREP WIDGET
        self.morning_widget = QWidget(self)
        morning_layout = QVBoxLayout(self.morning_widget)
        morning_layout.setContentsMargins(0, 0, 0, 0)
        morning_layout.setSpacing(12)
        
        hours_layout = QVBoxLayout()
        hours_header_layout = QHBoxLayout()
        hours_lbl = QLabel("Your Work Hours Today:", self)
        self.hours_val_lbl = QLabel("0 hrs", self)
        self.hours_val_lbl.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {ThemeManager.DARK_BROWN};")
        hours_header_layout.addWidget(hours_lbl)
        hours_header_layout.addWidget(self.hours_val_lbl, alignment=Qt.AlignRight)
        hours_layout.addLayout(hours_header_layout)
        
        self.hours_slider = QSlider(Qt.Horizontal, self)
        self.hours_slider.setRange(0, 24)
        self.hours_slider.setValue(8)
        self.hours_slider.setTickPosition(QSlider.TicksBelow)
        self.hours_slider.setTickInterval(4)
        self.hours_slider.valueChanged.connect(self.on_slider_changed)
        hours_layout.addWidget(self.hours_slider)
        
        self.energy_cost_lbl = QLabel("Energy Cost: 40.0 Energy", self)
        self.energy_cost_lbl.setStyleSheet("font-size: 12px; color: #666666;")
        hours_layout.addWidget(self.energy_cost_lbl)
        
        morning_layout.addLayout(hours_layout)
        
        self.open_btn = QPushButton("🍳 Open Restaurant & Start Simulation", self)
        self.open_btn.setObjectName("primary-action-btn")
        self.open_btn.setMinimumHeight(45)
        self.open_btn.clicked.connect(self.on_open_clicked)
        morning_layout.addWidget(self.open_btn)
        
        control_layout.addWidget(self.morning_widget)
        
        # 2. EVENING CHOICES WIDGET
        self.evening_widget = QWidget(self)
        evening_layout = QVBoxLayout(self.evening_widget)
        evening_layout.setContentsMargins(0, 0, 0, 0)
        evening_layout.setSpacing(12)
        
        self.evening_lbl = QLabel("🌓 Evening Phase - Time to unwind.", self)
        self.evening_lbl.setStyleSheet("font-style: italic; color: #555555;")
        evening_layout.addWidget(self.evening_lbl)
        
        self.tavern_btn = QPushButton("🍻 Visit Oakhaven Tavern (-15 Energy)", self)
        self.tavern_btn.setMinimumHeight(40)
        self.tavern_btn.clicked.connect(self.go_to_tavern.emit)
        evening_layout.addWidget(self.tavern_btn)
        
        self.sleep_btn = QPushButton("🛌 Go to Sleep & End Day", self)
        self.sleep_btn.setObjectName("primary-action-btn")
        self.sleep_btn.setMinimumHeight(40)
        self.sleep_btn.clicked.connect(self.sleep_clicked.emit)
        evening_layout.addWidget(self.sleep_btn)
        
        control_layout.addWidget(self.evening_widget)
        
        left_layout.addWidget(self.control_card)
        
        # Navigation Card
        nav_card = QFrame(self)
        nav_card.setObjectName("card-frame")
        nav_layout = QHBoxLayout(nav_card)
        nav_layout.setSpacing(15)
        
        self.biz_btn = QPushButton("💼 Manage Business", self)
        self.biz_btn.clicked.connect(self.manage_business.emit)
        nav_layout.addWidget(self.biz_btn)
        
        self.romance_btn = QPushButton("🌹 Personal Life", self)
        self.romance_btn.clicked.connect(self.personal_life.emit)
        nav_layout.addWidget(self.romance_btn)
        
        left_layout.addWidget(nav_card)
        
        main_layout.addLayout(left_layout, stretch=3)
        
        # RIGHT COLUMN: Current Objectives & Environment View
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        # Pixel Art Environment Banner
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
        
        # Initialize
        self.update_ui()

    def on_slider_changed(self, val: int):
        self.hours_val_lbl.setText(f"{val} hrs")
        cost = val * self.state.player.work_energy_cost_per_hour
        self.energy_cost_lbl.setText(f"Energy Cost: {cost:.1f} Energy")
        
        # Warning if energy exceeds limit
        if cost > self.state.player.energy:
            self.energy_cost_lbl.setStyleSheet("font-size: 12px; color: #E25E3E; font-weight: bold;")
            self.open_btn.setEnabled(False)
        else:
            self.energy_cost_lbl.setStyleSheet("font-size: 12px; color: #666666;")
            self.open_btn.setEnabled(True)

    def on_open_clicked(self):
        UIAudio.play_click()
        hours = self.hours_slider.value()
        self.restaurant_opened.emit(hours)

    def update_ui(self, evening_mode=False):
        p = self.state.player
        r = self.state.restaurant
        rom = self.state.romance
        h = self.state.house
        c = self.state.competitor
        
        # Toggle Morning vs Evening controls visibility
        self.morning_widget.setVisible(not evening_mode)
        self.evening_widget.setVisible(evening_mode)
        
        if evening_mode:
            # Tavern button check
            is_level_ok = r.level >= 3
            has_energy = p.energy >= 15
            self.tavern_btn.setEnabled(is_level_ok and has_energy)
            if not is_level_ok:
                self.tavern_btn.setText("🍻 Tavern Locked (Requires Level 3)")
            elif not has_energy:
                self.tavern_btn.setText("🍻 Too Exhausted for Tavern (Needs 15 Energy)")
            else:
                self.tavern_btn.setText("🍻 Visit Oakhaven Tavern (-15 Energy)")
                
        # Update energy readout
        self.energy_readout.setText(f"Your Energy: {p.energy:.1f}/{p.max_energy}")
        self.on_slider_changed(self.hours_slider.value())
        
        # Update competitor threat banner
        if c.is_active and not c.counter_marketing_active:
            self.threat_banner.setVisible(True)
        else:
            self.threat_banner.setVisible(False)
            
        # Update navigation button visibility
        self.romance_btn.setVisible(r.level >= 3)
        
        # Generate objectives content
        obj_text = ""
        if r.level == 0:
            obj_text = f"• Save <b>$100.00</b> to buy a Second-Hand Roadside Cart.<br/><br/>• Cook directly on the street to serve hungry passersby."
        elif r.level == 1:
            obj_text = f"• Save <b>$250.00</b> to upgrade to your Own Roadside Cart.<br/><br/>• Expand your customer capacity and daily earnings."
        elif r.level == 2:
            obj_text = f"• Save <b>$800.00</b> to upgrade to an Edge-of-Town Shop.<br/><br/>• Earn a proper counter, hire employees, and unlock the local Tavern."
        elif r.level == 3:
            obj_text = f"• Save <b>$2500.00</b> to upgrade to a full Town Restaurant.<br/><br/>• Visit the Tavern in the evening to socialize, date, and recruit employees."
        elif r.level == 4 and not h.purchased:
            obj_text = f"• Save <b>$4000.00</b> to purchase your first cozy House.<br/><br/>• Go on dates with <b>{rom.partner_name}</b> at the Tavern to boost romance!"
        elif r.level == 4 and h.purchased and not rom.is_co_owner:
            ring_str = "• Purchase a <b>Diamond Engagement Ring</b> ($2500.00) in Personal Life.<br/><br/>" if not rom.has_ring else ""
            obj_text = f"{ring_str}• Propose marriage & co-ownership to <b>{rom.partner_name}</b> (Requires Romance >= 75)."
        elif r.level == 4 and rom.is_co_owner and rom.wedding_tier == "None":
            obj_text = f"• Plan and host your <b>Wedding Ceremony</b> from the Personal Life menu to secure your future!"
        elif c.is_active:
            obj_text = (
                f"• Defend your life and restaurant from Chef Sebastian's aggressive smear campaigns!<br/><br/>"
                f"• Keep Reputation >= 60.0 and Romance >= 80.0.<br/><br/>"
                f"• Survive for <b>{10 - self.parent().days_survived_competitor if hasattr(self.parent(), 'days_survived_competitor') else 10} days</b> to secure victory."
            )
            
        self.obj_content.setText(f"<html><body>{obj_text}</body></html>")
